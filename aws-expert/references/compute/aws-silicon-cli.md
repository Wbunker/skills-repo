# AWS Custom Silicon — CLI Reference

For service concepts, see [aws-silicon-capabilities.md](aws-silicon-capabilities.md).

## AWS Graviton

```bash
# --- Launch a Graviton4 instance (M8g example) ---
aws ec2 run-instances \
  --image-id ami-0abcdef1234567890 \          # arm64 AMI required
  --instance-type m8g.xlarge \
  --key-name my-keypair \
  --subnet-id subnet-0abc123def456789 \
  --security-group-ids sg-0abc123def456789 \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=graviton4-app}]'

# Common Graviton instance types by generation:
#   Graviton2: m6g, c6g, r6g, t4g, x2gd, im4gn, is4gen
#   Graviton3: m7g, c7g, r7g, hpc7g
#   Graviton4: m8g, c8g, r8g

# --- List available Graviton instance types in a region ---
aws ec2 describe-instance-types \
  --filters "Name=processor-info.supported-architectures,Values=arm64" \
  --query 'InstanceTypes[*].{Type:InstanceType,vCPU:VCpuInfo.DefaultVCpus,MemGB:MemoryInfo.SizeInMiB}' \
  --output table

# --- Describe instance type offerings filtered by Graviton4 family ---
aws ec2 describe-instance-type-offerings \
  --filters "Name=instance-type,Values=m8g.*,c8g.*,r8g.*" \
  --query 'InstanceTypeOfferings[*].{Type:InstanceType,Location:Location}' \
  --output table

# Filter by specific architecture to confirm Arm64
aws ec2 describe-instance-types \
  --instance-types m8g.xlarge m8g.4xlarge c8g.2xlarge r8g.8xlarge \
  --query 'InstanceTypes[*].{Type:InstanceType,Arch:ProcessorInfo.SupportedArchitectures}'

# --- Graviton Savings Dashboard (Cost Explorer) ---
# Get Savings Plans utilization details (covers Graviton-backed Lambda, Fargate, EC2)
aws ce get-savings-plans-utilization-details \
  --time-period Start=2026-02-01,End=2026-03-01 \
  --filter '{"Dimensions":{"Key":"LINKED_ACCOUNT","Values":["123456789012"]}}' \
  --output json

# Get right-sizing recommendations (Compute Optimizer flags Graviton upgrade candidates)
aws compute-optimizer get-ec2-instance-recommendations \
  --recommendation-preferences '{"cpuVendorArchitectures":["AWS_ARM64"]}' \
  --query 'instanceRecommendations[*].{Instance:instanceArn,Finding:finding,RecommendedType:recommendationOptions[0].instanceType}'

# --- Launch a Lambda function on arm64 (Graviton) ---
aws lambda create-function \
  --function-name my-graviton-fn \
  --runtime python3.12 \
  --architectures arm64 \
  --role arn:aws:iam::123456789012:role/lambda-exec-role \
  --handler app.handler \
  --zip-file fileb://function.zip

# Update existing Lambda function to arm64
aws lambda update-function-configuration \
  --function-name my-graviton-fn \
  --architectures arm64
```

---

## AWS Trainium

```bash
# --- Launch a Trainium instance ---
# trn1.2xlarge: 2 Trainium1 chips — good for development and fine-tuning
aws ec2 run-instances \
  --image-id ami-0abcdef1234567890 \          # Deep Learning AMI (Neuron) — Amazon Linux 2023
  --instance-type trn1.2xlarge \
  --key-name my-keypair \
  --subnet-id subnet-0abc123def456789 \
  --security-group-ids sg-0abc123def456789 \
  --placement '{"GroupName":"my-placement-group"}' \  # placement group for trn1.32xlarge
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=trainium-training}]'

# trn1.32xlarge: 16 Trainium1 chips — large-scale distributed training
aws ec2 run-instances \
  --image-id ami-0abcdef1234567890 \
  --instance-type trn1.32xlarge \
  --key-name my-keypair \
  --subnet-id subnet-0abc123def456789 \
  --security-group-ids sg-0abc123def456789

# trn2.48xlarge: 16 Trainium2 chips — next-gen training
aws ec2 run-instances \
  --image-id ami-0abcdef1234567890 \
  --instance-type trn2.48xlarge \
  --key-name my-keypair \
  --subnet-id subnet-0abc123def456789 \
  --security-group-ids sg-0abc123def456789

# --- Neuron device management (run on the Trainium instance) ---
neuron-ls                        # list all attached Neuron devices and their NeuronCores
neuron-top                       # real-time utilization dashboard (NeuronCore %, memory, throughput)

# --- Neuron compiler (neuronx-cc) ---
# Compile a NEFF artifact from a traced PyTorch model
neuronx-cc compile \
  --framework PyTorch \
  --target trn1 \
  --model traced_model.pt \
  --output compiled_model.neff \
  --auto-cast matmul \           # cast matmul ops to BF16 automatically
  --verbose

# --- torch-neuronx: trace and compile a model (Python snippet) ---
# Run this Python on the Trainium instance to compile for deployment
# python3 compile_model.py
cat << 'EOF' > compile_model.py
import torch
import torch_neuronx

model = MyModel()
model.eval()

example_inputs = torch.zeros([1, 128], dtype=torch.long)  # adjust shape to model

# Trace the model (captures computation graph and compiles to NEFF)
traced_model = torch_neuronx.trace(model, example_inputs)
traced_model.save("compiled_model.pt")
print("Compilation complete: compiled_model.pt")
EOF

# --- Neuron profiler ---
neuron-profile capture --nn-model compiled_model.neff --output profile_output/
neuron-profile view --output profile_output/              # open flame graph in browser

# --- EKS: install Neuron device plugin (exposes aws.amazon.com/neuron resource) ---
kubectl apply -f https://raw.githubusercontent.com/aws-neuron/aws-neuron-sdk/master/src/k8/k8s-neuron-device-plugin.yml

# Verify Neuron devices are registered on nodes
kubectl get nodes -o custom-columns='NAME:.metadata.name,NEURON:.status.capacity.aws\.amazon\.com/neuron'

# Deploy a Trainium training job requesting Neuron devices
cat << 'EOF' | kubectl apply -f -
apiVersion: batch/v1
kind: Job
metadata:
  name: neuron-training-job
spec:
  template:
    spec:
      restartPolicy: OnFailure
      containers:
      - name: trainer
        image: 763104351884.dkr.ecr.us-east-1.amazonaws.com/pytorch-training-neuronx:latest
        command: ["python3", "train.py"]
        resources:
          limits:
            aws.amazon.com/neuron: 16    # request 16 Neuron devices (trn1.32xlarge)
EOF

# Install Neuron Scheduler Extension (for multi-chip bin-packing)
kubectl apply -f https://raw.githubusercontent.com/aws-neuron/aws-neuron-sdk/master/src/k8/k8s-neuron-scheduler.yml
```

---

## AWS Inferentia

```bash
# --- Launch an Inferentia2 instance ---
# inf2.xlarge: 1 Inferentia2 chip — single-model low-latency endpoint
aws ec2 run-instances \
  --image-id ami-0abcdef1234567890 \          # Deep Learning AMI (Neuron) — Amazon Linux 2023
  --instance-type inf2.xlarge \
  --key-name my-keypair \
  --subnet-id subnet-0abc123def456789 \
  --security-group-ids sg-0abc123def456789 \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=inferentia2-endpoint}]'

# inf2.48xlarge: 12 Inferentia2 chips, 384 GB HBM — largest LLM inference
aws ec2 run-instances \
  --image-id ami-0abcdef1234567890 \
  --instance-type inf2.48xlarge \
  --key-name my-keypair \
  --subnet-id subnet-0abc123def456789 \
  --security-group-ids sg-0abc123def456789

# inf1.24xlarge: 16 Inferentia1 chips — high-throughput legacy inference fleet
aws ec2 run-instances \
  --image-id ami-0abcdef1234567890 \
  --instance-type inf1.24xlarge \
  --key-name my-keypair \
  --subnet-id subnet-0abc123def456789 \
  --security-group-ids sg-0abc123def456789

# --- Neuron tools (same as Trainium; shared Neuron SDK) ---
neuron-ls                        # list Inferentia devices
neuron-top                       # real-time NeuronCore utilization

# --- Compile a model for Inferentia2 (Python snippet) ---
cat << 'EOF' > compile_inf2.py
import torch
import torch_neuronx
from transformers import AutoModelForCausalLM, AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3-8b")
model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3-8b")
model.eval()

# Create example inputs matching model's expected input shape
input_ids = torch.zeros([1, 512], dtype=torch.long)
attention_mask = torch.ones([1, 512], dtype=torch.long)
example_inputs = (input_ids, attention_mask)

# Trace and compile to NEFF for Inferentia2
traced_model = torch_neuronx.trace(model, example_inputs)
traced_model.save("llama3-8b-inf2.pt")
print("Compiled model saved: llama3-8b-inf2.pt")
EOF

# --- SageMaker: create endpoint with Inferentia2 instance ---
# Step 1: create endpoint configuration pointing to model artifact
aws sagemaker create-endpoint-config \
  --endpoint-config-name llama3-inf2-config \
  --production-variants '[{
    "VariantName": "AllTraffic",
    "ModelName": "llama3-8b-neuron",
    "InitialInstanceCount": 1,
    "InstanceType": "ml.inf2.48xlarge",
    "InitialVariantWeight": 1.0
  }]'

# Step 2: create the endpoint
aws sagemaker create-endpoint \
  --endpoint-name llama3-inf2-endpoint \
  --endpoint-config-name llama3-inf2-config \
  --tags Key=Environment,Value=production

# Wait for endpoint to be in service
aws sagemaker wait endpoint-in-service \
  --endpoint-name llama3-inf2-endpoint

# Describe endpoint status
aws sagemaker describe-endpoint \
  --endpoint-name llama3-inf2-endpoint \
  --query '{Status:EndpointStatus,InstanceType:ProductionVariants[0].CurrentInstanceType}'

# Invoke the endpoint
aws sagemaker-runtime invoke-endpoint \
  --endpoint-name llama3-inf2-endpoint \
  --content-type application/json \
  --body '{"inputs": "Tell me about AWS Inferentia"}' \
  response.json

# List SageMaker endpoints using inf2 instance types
aws sagemaker list-endpoints \
  --status-equals InService \
  --query 'Endpoints[*].EndpointName'
```

---

## AWS Nitro Enclaves

```bash
# --- Enable Nitro Enclaves on an existing instance (requires stop/start) ---
# Note: instance must be stopped first; not all instance types support enclaves
aws ec2 stop-instances --instance-ids i-0abc123def456789
aws ec2 wait instance-stopped --instance-ids i-0abc123def456789

aws ec2 modify-instance-attribute \
  --instance-id i-0abc123def456789 \
  --enclave-options Enabled=true

aws ec2 start-instances --instance-ids i-0abc123def456789

# Verify enclave support is enabled
aws ec2 describe-instances \
  --instance-ids i-0abc123def456789 \
  --query 'Reservations[0].Instances[0].EnclaveOptions'

# Launch a new instance with Nitro Enclaves enabled at launch
aws ec2 run-instances \
  --image-id ami-0abcdef1234567890 \
  --instance-type m5.xlarge \                  # must be Nitro-based instance
  --key-name my-keypair \
  --subnet-id subnet-0abc123def456789 \
  --enclave-options Enabled=true

# --- Build an Enclave Image File (EIF) from a Docker image ---
# Run on the parent EC2 instance (nitro-cli installed via Nitro Enclaves CLI package)
nitro-cli build-enclave \
  --docker-uri my-enclave-app:latest \
  --output-file my-enclave.eif
# Output includes: EIF file path, PCR0/PCR1/PCR2 measurements (used in KMS attestation policies)

# --- Run an enclave ---
nitro-cli run-enclave \
  --enclave-cid 16 \                           # vsock CID for parent-to-enclave communication
  --cpu-count 2 \                              # CPUs allocated to enclave (taken from parent instance)
  --memory 4096 \                              # MiB allocated to enclave
  --eif-path my-enclave.eif \
  --debug-mode                                 # enables console output (remove for production)

# Run without debug mode for production (no console access)
nitro-cli run-enclave \
  --enclave-cid 16 \
  --cpu-count 2 \
  --memory 4096 \
  --eif-path my-enclave.eif

# --- Describe running enclaves ---
nitro-cli describe-enclaves
# Returns: enclave ID, state, CPU/memory allocation, flags, enclave CID

# --- Terminate an enclave ---
nitro-cli terminate-enclave --enclave-id i-0abc123def456789-enc01234567890abcde

# --- KMS key policy for enclave attestation ---
# Allow KMS decrypt only when the calling enclave matches known PCR0 measurement
# Add this statement to a KMS key policy:
cat << 'EOF'
{
  "Effect": "Allow",
  "Principal": {"AWS": "arn:aws:iam::123456789012:role/enclave-role"},
  "Action": "kms:Decrypt",
  "Resource": "*",
  "Condition": {
    "StringEqualsIgnoreCase": {
      "kms:RecipientAttestation:PCR0": "abc123...measured_hash_of_enclave_image..."
    }
  }
}
EOF
```

---

## ENA Express / Aquila

```bash
# --- Enable ENA Express on an existing ENI ---
# Both source and destination ENIs must have ENA Express enabled for SRD to activate
aws ec2 modify-network-interface-attribute \
  --network-interface-id eni-0abc123def456789 \
  --ena-srd-specification 'EnaSrdEnabled=true'

# Enable ENA Express for UDP traffic as well (for latency-sensitive UDP workloads)
aws ec2 modify-network-interface-attribute \
  --network-interface-id eni-0abc123def456789 \
  --ena-srd-specification 'EnaSrdEnabled=true,EnaSrdUdpSpecification={EnaSrdUdpEnabled=true}'

# --- Describe ENA Express status on an ENI ---
aws ec2 describe-network-interface-attribute \
  --network-interface-id eni-0abc123def456789 \
  --attribute enaSrdSpecification

# --- Enable ENA Express at instance launch (via network interface specification) ---
aws ec2 run-instances \
  --image-id ami-0abcdef1234567890 \
  --instance-type c6gn.16xlarge \              # Aquila-backed instance (C6gn, C6in, C7gn, Hpc7g)
  --key-name my-keypair \
  --network-interfaces '[{
    "DeviceIndex": 0,
    "SubnetId": "subnet-0abc123def456789",
    "Groups": ["sg-0abc123def456789"],
    "EnaSrdSpecification": {
      "EnaSrdEnabled": true,
      "EnaSrdUdpSpecification": {"EnaSrdUdpEnabled": false}
    }
  }]'

# --- Verify ENA Express is active between two instances ---
# Check that both instances are on supported instance types
aws ec2 describe-instance-types \
  --instance-types c6gn.16xlarge c7gn.16xlarge c6in.32xlarge hpc7g.16xlarge \
  --query 'InstanceTypes[*].{Type:InstanceType,EnaSupport:NetworkInfo.EnaSupport,MaxBandwidthGbps:NetworkInfo.MaximumNetworkBandwidthInGbps}'

# --- List all ENIs with ENA Express enabled ---
aws ec2 describe-network-interfaces \
  --filters "Name=ena-srd-specification.ena-srd-enabled,Values=true" \
  --query 'NetworkInterfaces[*].{ENI:NetworkInterfaceId,InstanceId:Attachment.InstanceId,ENA_SRD:EnaSrdSpecification}'

# --- EFA (for HPC / MPI workloads — OS-bypass, requires libfabric) ---
# Launch an EFA-enabled instance (separate from ENA Express; used for HPC/ML training)
aws ec2 run-instances \
  --image-id ami-0abcdef1234567890 \
  --instance-type hpc7g.16xlarge \
  --key-name my-keypair \
  --network-interfaces '[{
    "DeviceIndex": 0,
    "SubnetId": "subnet-0abc123def456789",
    "Groups": ["sg-0abc123def456789"],
    "InterfaceType": "efa"                     # EFA interface type (not standard)
  }]' \
  --placement '{"GroupName":"my-cluster-pg"}'  # cluster placement group required for EFA

# Describe EFA-enabled instance types
aws ec2 describe-instance-types \
  --filters "Name=network-info.efa-supported,Values=true" \
  --query 'InstanceTypes[*].{Type:InstanceType,EFA:NetworkInfo.EfaSupported,MaxBW:NetworkInfo.MaximumNetworkBandwidthInGbps}' \
  --output table
```
