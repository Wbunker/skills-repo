# AWS Vision & NLP Services — CLI Reference
For service concepts, see [vision-nlp-services-capabilities.md](vision-nlp-services-capabilities.md).

## Amazon Rekognition

```bash
# --- Image Analysis ---
# Detect labels (objects, scenes, activities)
aws rekognition detect-labels \
  --image '{"S3Object":{"Bucket":"my-bucket","Name":"photo.jpg"}}' \
  --max-labels 20 \
  --min-confidence 70

# Detect labels from local file
aws rekognition detect-labels \
  --image '{"Bytes":"'$(base64 -i photo.jpg)'"}' \
  --max-labels 10

# Detect faces with attributes
aws rekognition detect-faces \
  --image '{"S3Object":{"Bucket":"my-bucket","Name":"faces.jpg"}}' \
  --attributes ALL

# Compare faces (source vs. target)
aws rekognition compare-faces \
  --source-image '{"S3Object":{"Bucket":"my-bucket","Name":"source.jpg"}}' \
  --target-image '{"S3Object":{"Bucket":"my-bucket","Name":"target.jpg"}}' \
  --similarity-threshold 80

# Recognize celebrities
aws rekognition recognize-celebrities \
  --image '{"S3Object":{"Bucket":"my-bucket","Name":"celebrities.jpg"}}'

# Detect text (OCR)
aws rekognition detect-text \
  --image '{"S3Object":{"Bucket":"my-bucket","Name":"sign.jpg"}}'

# Detect moderation labels (unsafe content)
aws rekognition detect-moderation-labels \
  --image '{"S3Object":{"Bucket":"my-bucket","Name":"ugc-image.jpg"}}' \
  --min-confidence 60

# Detect custom labels
aws rekognition detect-custom-labels \
  --project-version-arn arn:aws:rekognition:us-east-1:123456789012:project/my-project/version/v1/TIMESTAMP \
  --image '{"S3Object":{"Bucket":"my-bucket","Name":"product.jpg"}}'

# --- Face Collections ---
aws rekognition create-collection --collection-id my-face-collection
aws rekognition list-collections
aws rekognition describe-collection --collection-id my-face-collection

# Index faces into collection
aws rekognition index-faces \
  --collection-id my-face-collection \
  --image '{"S3Object":{"Bucket":"my-bucket","Name":"employee.jpg"}}' \
  --external-image-id employee-john-doe \
  --detection-attributes ALL \
  --max-faces 1

# Search faces by image
aws rekognition search-faces-by-image \
  --collection-id my-face-collection \
  --image '{"S3Object":{"Bucket":"my-bucket","Name":"visitor.jpg"}}' \
  --max-faces 5 \
  --face-match-threshold 85

# Search faces by face ID
aws rekognition search-faces \
  --collection-id my-face-collection \
  --face-id FACE_ID \
  --max-faces 10

aws rekognition list-faces --collection-id my-face-collection
aws rekognition delete-faces --collection-id my-face-collection --face-ids '["FACE_ID_1","FACE_ID_2"]'
aws rekognition delete-collection --collection-id my-face-collection

# --- Video Analysis (async) ---
# Start label detection on stored video
aws rekognition start-label-detection \
  --video '{"S3Object":{"Bucket":"my-bucket","Name":"video.mp4"}}' \
  --notification-channel '{"SNSTopicArn":"arn:aws:sns:us-east-1:123456789012:rekognition-results","RoleArn":"arn:aws:iam::123456789012:role/RekognitionRole"}' \
  --min-confidence 70

aws rekognition get-label-detection --job-id JOB_ID --sort-by TIMESTAMP

# Start face detection in video
aws rekognition start-face-detection \
  --video '{"S3Object":{"Bucket":"my-bucket","Name":"video.mp4"}}' \
  --notification-channel '{"SNSTopicArn":"arn:aws:sns:us-east-1:123456789012:rekognition-results","RoleArn":"arn:aws:iam::123456789012:role/RekognitionRole"}'
aws rekognition get-face-detection --job-id JOB_ID

# Start content moderation on video
aws rekognition start-content-moderation \
  --video '{"S3Object":{"Bucket":"my-bucket","Name":"video.mp4"}}' \
  --min-confidence 60
aws rekognition get-content-moderation --job-id JOB_ID

# Start text detection in video
aws rekognition start-text-detection \
  --video '{"S3Object":{"Bucket":"my-bucket","Name":"video.mp4"}}'
aws rekognition get-text-detection --job-id JOB_ID

# Start celebrity recognition in video
aws rekognition start-celebrity-recognition \
  --video '{"S3Object":{"Bucket":"my-bucket","Name":"video.mp4"}}'
aws rekognition get-celebrity-recognition --job-id JOB_ID
```

---

## Amazon Comprehend

```bash
# --- Real-time Detection ---
# Detect entities
aws comprehend detect-entities \
  --text "Amazon was founded by Jeff Bezos in Bellevue, Washington on July 5, 1994." \
  --language-code en

# Detect key phrases
aws comprehend detect-key-phrases \
  --text "Machine learning is transforming the way businesses operate." \
  --language-code en

# Detect sentiment
aws comprehend detect-sentiment \
  --text "I absolutely love this product, it exceeded all my expectations!" \
  --language-code en

# Detect syntax (parts of speech)
aws comprehend detect-syntax \
  --text "The quick brown fox jumps over the lazy dog." \
  --language-code en

# Detect dominant language
aws comprehend detect-dominant-language \
  --text "Bonjour, comment allez-vous aujourd'hui?"

# Detect PII
aws comprehend detect-pii-entities \
  --text "My SSN is 123-45-6789 and my email is john@example.com." \
  --language-code en

# Detect targeted sentiment
aws comprehend detect-targeted-sentiment \
  --text "The camera quality is excellent but the battery life is terrible." \
  --language-code en

# --- Batch Detection (up to 25 documents) ---
aws comprehend batch-detect-entities \
  --text-list '["Jeff Bezos founded Amazon.","Elon Musk leads Tesla and SpaceX."]' \
  --language-code en

aws comprehend batch-detect-sentiment \
  --text-list '["I love this!","This is terrible.","It is okay."]' \
  --language-code en

aws comprehend batch-detect-key-phrases \
  --text-list '["Cloud computing is the future.","AI is transforming industries."]' \
  --language-code en

aws comprehend batch-detect-syntax \
  --text-list '["She sells seashells.","He runs every day."]' \
  --language-code en

# --- Async Jobs (large document sets from S3) ---
aws comprehend start-entities-detection-job \
  --job-name entities-job \
  --data-access-role-arn arn:aws:iam::123456789012:role/ComprehendRole \
  --language-code en \
  --input-data-config '{"S3Uri":"s3://my-bucket/input/","InputFormat":"ONE_DOC_PER_FILE"}' \
  --output-data-config '{"S3Uri":"s3://my-bucket/output/"}'

aws comprehend start-sentiment-detection-job \
  --job-name sentiment-job \
  --data-access-role-arn arn:aws:iam::123456789012:role/ComprehendRole \
  --language-code en \
  --input-data-config '{"S3Uri":"s3://my-bucket/input/","InputFormat":"ONE_DOC_PER_LINE"}' \
  --output-data-config '{"S3Uri":"s3://my-bucket/output/"}'

aws comprehend start-key-phrases-detection-job \
  --job-name key-phrases-job \
  --data-access-role-arn arn:aws:iam::123456789012:role/ComprehendRole \
  --language-code en \
  --input-data-config '{"S3Uri":"s3://my-bucket/input/"}' \
  --output-data-config '{"S3Uri":"s3://my-bucket/output/"}'

aws comprehend describe-entities-detection-job --job-id JOB_ID
aws comprehend list-entities-detection-jobs

# --- Custom Classification ---
aws comprehend create-document-classifier \
  --document-classifier-name my-classifier \
  --data-access-role-arn arn:aws:iam::123456789012:role/ComprehendRole \
  --language-code en \
  --input-data-config '{"DataFormat":"COMPREHEND_CSV","S3Uri":"s3://my-bucket/training-data/"}' \
  --mode MULTI_CLASS

aws comprehend describe-document-classifier --document-classifier-arn CLASSIFIER_ARN
aws comprehend list-document-classifiers

# Start a classification job with custom model
aws comprehend start-document-classification-job \
  --job-name classify-docs \
  --document-classifier-arn CLASSIFIER_ARN \
  --data-access-role-arn arn:aws:iam::123456789012:role/ComprehendRole \
  --input-data-config '{"S3Uri":"s3://my-bucket/docs-to-classify/","InputFormat":"ONE_DOC_PER_FILE"}' \
  --output-data-config '{"S3Uri":"s3://my-bucket/classification-output/"}'

aws comprehend describe-document-classification-job --job-id JOB_ID
aws comprehend delete-document-classifier --document-classifier-arn CLASSIFIER_ARN

# --- Custom Entity Recognizer ---
aws comprehend create-entity-recognizer \
  --recognizer-name my-ner-model \
  --data-access-role-arn arn:aws:iam::123456789012:role/ComprehendRole \
  --language-code en \
  --input-data-config '{"DataFormat":"COMPREHEND_CSV","EntityTypes":[{"Type":"PRODUCT_CODE"},{"Type":"PART_NUMBER"}],"Documents":{"S3Uri":"s3://my-bucket/ner-documents/"},"Annotations":{"S3Uri":"s3://my-bucket/ner-annotations/"}}'

aws comprehend describe-entity-recognizer --entity-recognizer-arn RECOGNIZER_ARN
aws comprehend list-entity-recognizers
aws comprehend delete-entity-recognizer --entity-recognizer-arn RECOGNIZER_ARN

# Deploy custom model as real-time endpoint
aws comprehend create-endpoint \
  --endpoint-name my-classifier-endpoint \
  --model-arn CLASSIFIER_ARN \
  --desired-inference-units 1
aws comprehend classify-document \
  --endpoint-arn ENDPOINT_ARN \
  --text "This document is about a software license renewal."
```

---

## Amazon Textract

```bash
# --- Synchronous Operations ---
# Detect text from S3 object
aws textract detect-document-text \
  --document '{"S3Object":{"Bucket":"my-bucket","Name":"document.pdf"}}'

# Detect text from local file
aws textract detect-document-text \
  --document '{"Bytes":"'$(base64 -i document.jpg)'"}'

# Analyze document (forms, tables, signatures)
aws textract analyze-document \
  --document '{"S3Object":{"Bucket":"my-bucket","Name":"form.pdf"}}' \
  --feature-types '["FORMS","TABLES"]'

# Analyze document with queries
aws textract analyze-document \
  --document '{"S3Object":{"Bucket":"my-bucket","Name":"application-form.pdf"}}' \
  --feature-types '["QUERIES"]' \
  --queries-config '{"Queries":[{"Text":"What is the applicant name?","Alias":"name"},{"Text":"What is the date of birth?","Alias":"dob"},{"Text":"What is the total amount?","Alias":"amount"}]}'

# Analyze expense (invoices, receipts)
aws textract analyze-expense \
  --document '{"S3Object":{"Bucket":"my-bucket","Name":"invoice.pdf"}}'

# Analyze ID document
aws textract analyze-id \
  --document-pages '[{"S3Object":{"Bucket":"my-bucket","Name":"drivers-license.jpg"}}]'

# --- Asynchronous Operations (multi-page documents) ---
# Start async document analysis
aws textract start-document-analysis \
  --document-location '{"S3Object":{"Bucket":"my-bucket","Name":"multi-page-form.pdf"}}' \
  --feature-types '["FORMS","TABLES"]' \
  --notification-channel '{"SNSTopicArn":"arn:aws:sns:us-east-1:123456789012:textract-results","RoleArn":"arn:aws:iam::123456789012:role/TextractRole"}' \
  --output-config '{"S3Bucket":"my-bucket","S3Prefix":"textract-output/"}'

aws textract get-document-analysis --job-id JOB_ID
# Paginate results
aws textract get-document-analysis --job-id JOB_ID --next-token NEXT_TOKEN

# Start async text detection
aws textract start-document-text-detection \
  --document-location '{"S3Object":{"Bucket":"my-bucket","Name":"large-document.pdf"}}' \
  --notification-channel '{"SNSTopicArn":"arn:aws:sns:us-east-1:123456789012:textract-results","RoleArn":"arn:aws:iam::123456789012:role/TextractRole"}'

aws textract get-document-text-detection --job-id JOB_ID

# Start async expense analysis
aws textract start-expense-analysis \
  --document-location '{"S3Object":{"Bucket":"my-bucket","Name":"batch-invoices.pdf"}}'
aws textract get-expense-analysis --job-id JOB_ID

# --- Lending Document Analysis ---
aws textract start-lending-analysis \
  --document-location '{"S3Object":{"Bucket":"my-bucket","Name":"mortgage-package.pdf"}}' \
  --output-config '{"S3Bucket":"my-bucket","S3Prefix":"lending-output/"}'
aws textract get-lending-analysis --job-id JOB_ID
aws textract get-lending-analysis-summary --job-id JOB_ID
```

---

## Amazon Transcribe

```bash
# --- Batch Transcription ---
aws transcribe start-transcription-job \
  --transcription-job-name my-transcription \
  --media '{"MediaFileUri":"s3://my-bucket/audio/interview.mp4"}' \
  --media-format mp4 \
  --language-code en-US \
  --output-bucket-name my-bucket \
  --output-key transcripts/interview-transcript.json

# With speaker diarization
aws transcribe start-transcription-job \
  --transcription-job-name diarization-job \
  --media '{"MediaFileUri":"s3://my-bucket/audio/meeting.mp3"}' \
  --media-format mp3 \
  --language-code en-US \
  --output-bucket-name my-bucket \
  --settings '{"ShowSpeakerLabels":true,"MaxSpeakerLabels":4}'

# With custom vocabulary
aws transcribe start-transcription-job \
  --transcription-job-name custom-vocab-job \
  --media '{"MediaFileUri":"s3://my-bucket/audio/technical-talk.mp3"}' \
  --media-format mp3 \
  --language-code en-US \
  --output-bucket-name my-bucket \
  --settings '{"VocabularyName":"my-tech-vocabulary"}'

# With PII redaction
aws transcribe start-transcription-job \
  --transcription-job-name redacted-job \
  --media '{"MediaFileUri":"s3://my-bucket/audio/customer-call.mp3"}' \
  --media-format mp3 \
  --language-code en-US \
  --output-bucket-name my-bucket \
  --content-redaction '{"RedactionType":"PII","RedactionOutput":"redacted"}'

# With automatic language identification
aws transcribe start-transcription-job \
  --transcription-job-name auto-language-job \
  --media '{"MediaFileUri":"s3://my-bucket/audio/unknown-language.mp3"}' \
  --media-format mp3 \
  --identify-language \
  --output-bucket-name my-bucket

aws transcribe get-transcription-job --transcription-job-name my-transcription
aws transcribe list-transcription-jobs
aws transcribe list-transcription-jobs --status COMPLETED
aws transcribe delete-transcription-job --transcription-job-name my-transcription

# --- Custom Vocabulary ---
aws transcribe create-vocabulary \
  --vocabulary-name my-tech-vocabulary \
  --language-code en-US \
  --vocabulary-file-uri s3://my-bucket/vocab/custom-terms.txt
aws transcribe get-vocabulary --vocabulary-name my-tech-vocabulary
aws transcribe list-vocabularies
aws transcribe delete-vocabulary --vocabulary-name my-tech-vocabulary

# --- Custom Language Model ---
aws transcribe create-language-model \
  --language-code en-US \
  --base-model-name NarrowBand \
  --model-name my-custom-model \
  --input-data-config '{"S3Uri":"s3://my-bucket/lm-training-data/","TuningDataS3Uri":"s3://my-bucket/lm-tuning-data/","DataAccessRoleArn":"arn:aws:iam::123456789012:role/TranscribeRole"}'
aws transcribe list-language-models
aws transcribe describe-language-model --model-name my-custom-model

# --- Medical Transcription ---
aws transcribe start-medical-transcription-job \
  --medical-transcription-job-name my-medical-job \
  --media '{"MediaFileUri":"s3://my-bucket/audio/doctor-dictation.mp3"}' \
  --media-format mp3 \
  --language-code en-US \
  --output-bucket-name my-bucket \
  --specialty PRIMARYCARE \
  --type DICTATION

# Types: DICTATION (doctor notes), CONVERSATION (patient visits)
# Specialties: PRIMARYCARE, CARDIOLOGY, NEUROLOGY, ONCOLOGY, RADIOLOGY, UROLOGY
aws transcribe get-medical-transcription-job --medical-transcription-job-name my-medical-job
aws transcribe list-medical-transcription-jobs

# --- Call Analytics ---
aws transcribe start-call-analytics-job \
  --call-analytics-job-name my-call-analytics \
  --media '{"MediaFileUri":"s3://my-bucket/calls/call-recording.mp3"}' \
  --output-location s3://my-bucket/call-analytics-output/ \
  --data-access-role-arn arn:aws:iam::123456789012:role/TranscribeRole \
  --channel-definitions '[{"ChannelId":0,"ParticipantRole":"AGENT"},{"ChannelId":1,"ParticipantRole":"CUSTOMER"}]'

aws transcribe get-call-analytics-job --call-analytics-job-name my-call-analytics
aws transcribe list-call-analytics-jobs
```

---

## Amazon Translate

```bash
# --- Real-time Translation ---
aws translate translate-text \
  --text "Hello, how are you today?" \
  --source-language-code en \
  --target-language-code es

# Auto-detect source language
aws translate translate-text \
  --text "Bonjour tout le monde" \
  --source-language-code auto \
  --target-language-code en

# With custom terminology
aws translate translate-text \
  --text "The Amazon CloudFront CDN delivers content globally." \
  --source-language-code en \
  --target-language-code de \
  --terminology-names '["aws-product-names"]'

# --- Batch Translation ---
aws translate start-text-translation-job \
  --job-name batch-translate-job \
  --data-access-role-arn arn:aws:iam::123456789012:role/TranslateRole \
  --input-data-config '{"S3Uri":"s3://my-bucket/docs-to-translate/","ContentType":"text/html"}' \
  --output-data-config '{"S3Uri":"s3://my-bucket/translated-docs/"}' \
  --source-language-code en \
  --target-language-codes '["es","fr","de","ja","pt"]'

aws translate describe-text-translation-job --job-id JOB_ID
aws translate list-text-translation-jobs
aws translate stop-text-translation-job --job-id JOB_ID

# --- Custom Terminology ---
aws translate import-terminology \
  --name aws-product-names \
  --merge-strategy OVERWRITE \
  --terminology-data '{"File":"'$(base64 -i terminology.csv)'","Format":"CSV"}' \
  --description "AWS product name translations"

# Terminology CSV format:
# en,es,fr
# Amazon S3,Amazon S3,Amazon S3
# CloudFront,CloudFront,CloudFront

aws translate get-terminology --name aws-product-names --terminology-data-format CSV
aws translate list-terminologies
aws translate delete-terminology --name aws-product-names

# --- Parallel Data (active customization) ---
aws translate create-parallel-data \
  --name customer-support-parallel-data \
  --parallel-data-config '{"S3Uri":"s3://my-bucket/parallel-data/","Format":"TMX"}' \
  --description "Customer support translation examples"

aws translate get-parallel-data --name customer-support-parallel-data
aws translate list-parallel-data
aws translate update-parallel-data \
  --name customer-support-parallel-data \
  --parallel-data-config '{"S3Uri":"s3://my-bucket/parallel-data-v2/","Format":"TMX"}'
aws translate delete-parallel-data --name customer-support-parallel-data
```

---

## Amazon Polly

```bash
# --- Synthesize Speech ---
# Basic text-to-speech (save to file)
aws polly synthesize-speech \
  --text "Hello, welcome to Amazon Polly!" \
  --voice-id Joanna \
  --output-format mp3 \
  speech.mp3

# Using neural voice engine
aws polly synthesize-speech \
  --text "This is a neural text-to-speech example." \
  --voice-id Matthew \
  --engine neural \
  --output-format mp3 \
  speech.mp3

# With SSML markup
aws polly synthesize-speech \
  --text-type ssml \
  --text '<speak>Welcome to <emphasis level="strong">Amazon Polly</emphasis>. <break time="500ms"/> This sentence has a pause. <prosody rate="slow">This part is spoken slowly.</prosody></speak>' \
  --voice-id Joanna \
  --engine neural \
  --output-format mp3 \
  speech.mp3

# With speech marks (for lip sync / karaoke)
aws polly synthesize-speech \
  --text "The quick brown fox." \
  --voice-id Joanna \
  --output-format json \
  --speech-mark-types '["word","sentence","viseme"]' \
  speech-marks.json

# With custom lexicon
aws polly synthesize-speech \
  --text "The W3C publishes the HTML specification." \
  --voice-id Joanna \
  --engine neural \
  --output-format mp3 \
  --lexicon-names '["tech-acronyms"]' \
  speech.mp3

# With Newscaster speaking style (neural only)
aws polly synthesize-speech \
  --text "Breaking news: AWS announces new AI services." \
  --voice-id Matthew \
  --engine neural \
  --output-format mp3 \
  news.mp3

# --- List Available Voices ---
aws polly describe-voices
aws polly describe-voices --engine neural
aws polly describe-voices --language-code es-US
aws polly describe-voices --engine neural --language-code en-US

# --- Lexicons ---
# Create/update a pronunciation lexicon (PLS format)
aws polly put-lexicon \
  --name tech-acronyms \
  --content '<?xml version="1.0" encoding="UTF-8"?><lexicon version="1.0" xmlns="http://www.w3.org/2005/01/pronunciation-lexicon" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.w3.org/2005/01/pronunciation-lexicon http://www.w3.org/TR/2007/CR-pronunciation-lexicon-20071212/pls.xsd" alphabet="ipa" xml:lang="en-US"><lexeme><grapheme>W3C</grapheme><alias>World Wide Web Consortium</alias></lexeme><lexeme><grapheme>AWS</grapheme><phoneme>eɪdʌblju:ɛs</phoneme></lexeme></lexicon>'

aws polly get-lexicon --name tech-acronyms
aws polly list-lexicons
aws polly delete-lexicon --name tech-acronyms

# --- Async Speech Synthesis (for long text) ---
aws polly start-speech-synthesis-task \
  --text file://long-document.txt \
  --voice-id Joanna \
  --engine neural \
  --output-format mp3 \
  --output-s3-bucket-name my-polly-output \
  --output-s3-key-prefix audio/

aws polly get-speech-synthesis-task --task-id TASK_ID
aws polly list-speech-synthesis-tasks
```
