# Gemma Gotchas and Known Issues

## Critical Issues (Check Before Building)

### 1. CUDA 13.2 Corrupts GGUF Outputs

**Symptom**: Random mid-generation typos, garbled tokens, character substitutions during otherwise normal generation.

**Cause**: A bug in CUDA 13.2 affects GGUF token sampling in llama.cpp.

**Fix**: Downgrade to CUDA 13.0.

```bash
# Check your CUDA version
nvcc --version

# Install CUDA 13.0 via the CUDA toolkit archive if needed
```

**Also check your llama.cpp build version**: A separate build-level bug in llama.cpp builds from the b28xx range (late March 2026) produces the same symptom. Fix: use b3000+ for general inference, or b3447+ for flash attention support.

```bash
llama-server --version
# If in b28xx range, update immediately
```

These may be two distinct bugs producing identical symptoms — check both CUDA version and llama.cpp build if you see random mid-generation corruption.

---

### 2. `--jinja` Flag Required for Tool Calling in llama.cpp

**Symptom**: Tool-calling workflows loop indefinitely (15,000+ tokens), emit malformed `<tool_call>` tags, or never emit `<end_of_turn>`.

**Cause**: Without `--jinja`, llama.cpp uses a generic chat template that does not handle Gemma 4's tool-call format.

**Fix**: Always pass `--jinja` when running the llama.cpp server for agentic tasks:

```bash
./build/bin/llama-server -m model.gguf --jinja --n-gpu-layers 99
```

---

### 3. Thinking Tag Leakage (OpenWebUI + llama.cpp)

**Symptom**: Model outputs its internal `<think>...</think>` reasoning process to the user instead of suppressing it.

**Cause**: The default Jinja template doesn't suppress thinking output in all UIs.

**Fix**: Install a community Jinja template that strips thinking tags before the final response. In OpenWebUI, check the model settings for "System Prompt" or "Template Override" options.

Manual stripping in code:

```python
import re

def clean_response(text: str) -> str:
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
```

---

### 4. Repetition Loops at Long Lists

**Symptom**: Gemma 4 26B A4B starts looping at list item 14+ (e.g., "14. ... 15. ... 14. ... 15...").

**Cause**: Known model behavior, most common in structured list generation tasks.

**Mitigation**:
- Use `temperature=1.0` (not lower — lower temperatures increase loop likelihood)
- Add `repetition_penalty=1.1` in your generation config
- Implement loop detection: check if the last 50 tokens repeat within the last 200 tokens

```python
def detect_loop(token_ids: list, window: int = 50, lookback: int = 200) -> bool:
    if len(token_ids) < window + lookback:
        return False
    recent = token_ids[-window:]
    prior = token_ids[-(window + lookback):-window]
    # Check if recent sequence appears in prior window
    recent_str = str(recent)
    prior_str = str(prior)
    return recent_str in prior_str
```

---

### 5. Ollama: `think=false` + `format` Conflict

**Symptom**: Setting both `think=false` and structured output (`format`) together causes unexpected behavior or errors.

**Cause**: Open bug in Ollama — these two options conflict internally.

**Fix**: Use one or the other, not both simultaneously. For structured output without thinking, omit the `think` parameter entirely.

---

### 6. MoE Full VRAM Requirement

**Symptom**: Expecting Gemma 4 26B to use less VRAM because it's MoE, then running out of memory.

**Clarification**: MoE activates ~3.8B parameters **per token**, but the **full 26B parameters must be loaded into VRAM**. The memory savings vs. a dense 26B model are in inference compute (FLOPs), not in memory usage.

**Real VRAM usage**: ~18 GB for Q3_K_M quant + KV cache for 26B A4B.

---

### 7. vLLM FlashAttention Fallback

**Symptom**: Lower-than-expected throughput with vLLM for Gemma 4 MoE.

**Cause**: vLLM falls back from FlashAttention to a slower attention implementation due to Gemma 4's heterogeneous attention head dimensions in the MoE architecture.

**Detection**:

```bash
# Check vLLM logs for:
# "WARNING: FlashAttention not supported, falling back to..."
```

**Mitigation**: Use llama.cpp with `--flash-attn` instead of vLLM for better Gemma 4 performance. If vLLM is required, monitor throughput and set GPU utilization alerts.

---

### 8. RAG Context Override

**Symptom**: Building a RAG pipeline and seeing higher-than-expected hallucination rates — the model answers from its training knowledge instead of the retrieved documents.

**Cause**: Gemma 4 tends to prioritize its internal knowledge when it "recognizes" the topic, even when contradicting retrieved context.

**Fix**: Use an explicit instruction in the system prompt:

```
System: Answer ONLY using the provided documents. If the answer is not in the documents, say "I don't have this information." Do not use your general knowledge.
```

Test your RAG pipeline explicitly with questions whose answers conflict with the model's training data to measure override effectiveness before deploying.

---

### 9. Thinking Tags Between Tool Calls

**Symptom**: Stripping thinking tags aggressively causes agentic chains to lose reasoning context and degrade.

**Rule**: Strip `<think>...</think>` content **between conversation turns** (before presenting to user), but **preserve it between tool calls within the same turn**. The model's reasoning about a tool call is needed when it processes the tool result.

---

### 10. Chat Template Required

**Symptom**: Fine-tuned model or inference output is lower quality or ignores turn structure.

**Cause**: Gemma requires its specific chat template (`<start_of_turn>user\n...<end_of_turn>\n<start_of_turn>model\n`). Constructing prompts without it causes degraded behavior.

**Fix**: Always use `tokenizer.apply_chat_template()` in HuggingFace, or use the Ollama/llama.cpp native chat endpoint (not raw completions).

---

---

### 11. Python Coding Task Quality Profile (vs. Proprietary Models)

Gemma 4 31B handles ~75–80% of typical Python coding tasks correctly on first attempt vs. Claude Opus 4.6. Specific failure patterns:

**Debugging — multi-file root cause**: Identifies root cause correctly ~4/5 tasks. On complex bugs spanning multiple files, identifies the symptom rather than the underlying cause and requires a follow-up prompt. Use explicit "find the root cause in all related files" framing.

**Test writing — edge case coverage**: Generates solid happy-path tests but misses edge cases that only appear under specific conditions. Fix: explicitly enumerate edge cases to cover in the prompt.

**Feature writing — project-specific naming**: May miss project-specific naming conventions when generating new code. Mitigated by providing the full codebase context via the 256K context window rather than summarizing patterns.

**Refactoring**: Comparable to GPT-5.4; behind Gemini 3.1 Pro. Produces readable separation of concerns; naming choices are reasonable but not as nuanced as frontier models.

**Takeaway**: Gemma 4 follows detailed instructions well — compensate for weaknesses by being more explicit in prompts, not by switching models.

---

## Quick Diagnostic Checklist

Before filing a bug or asking for help, check:

- [ ] CUDA version is 13.0, not 13.2
- [ ] `--jinja` flag is present in llama.cpp command for tool calling
- [ ] `temperature=1.0` (not lower)
- [ ] Using chat endpoint, not raw completions endpoint
- [ ] MoE model loaded entirely in VRAM (not split across CPU/GPU for dense layers only)
- [ ] Chat template applied (not raw prompt construction)
- [ ] For RAG: explicit system prompt instruction to prioritize retrieved context
