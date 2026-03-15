# AWS Amazon SageMaker — CLI Reference
For service concepts, see [sagemaker-capabilities.md](sagemaker-capabilities.md).

## Amazon SageMaker

```bash
# --- Training Jobs ---
aws sagemaker create-training-job \
  --training-job-name my-training-job \
  --algorithm-specification '{"TrainingImage":"763104351884.dkr.ecr.us-east-1.amazonaws.com/pytorch-training:2.1.0-gpu-py310-cu121-ubuntu20.04-sagemaker","TrainingInputMode":"File"}' \
  --role-arn arn:aws:iam::123456789012:role/SageMakerRole \
  --input-data-config '[{"ChannelName":"training","DataSource":{"S3DataSource":{"S3DataType":"S3Prefix","S3Uri":"s3://my-bucket/train/","S3DataDistributionType":"FullyReplicated"}},"ContentType":"text/csv"}]' \
  --output-data-config '{"S3OutputPath":"s3://my-bucket/output/"}' \
  --resource-config '{"InstanceType":"ml.p3.2xlarge","InstanceCount":1,"VolumeSizeInGB":50}' \
  --stopping-condition '{"MaxRuntimeInSeconds":3600}' \
  --hyper-parameters '{"epochs":"10","learning-rate":"0.001","batch-size":"32"}'

# Training with Spot instances
aws sagemaker create-training-job \
  --training-job-name spot-training-job \
  --algorithm-specification '{"TrainingImage":"IMAGE_URI","TrainingInputMode":"File"}' \
  --role-arn arn:aws:iam::123456789012:role/SageMakerRole \
  --input-data-config '[{"ChannelName":"training","DataSource":{"S3DataSource":{"S3DataType":"S3Prefix","S3Uri":"s3://my-bucket/train/"}}}]' \
  --output-data-config '{"S3OutputPath":"s3://my-bucket/output/"}' \
  --resource-config '{"InstanceType":"ml.p3.2xlarge","InstanceCount":1,"VolumeSizeInGB":50}' \
  --stopping-condition '{"MaxRuntimeInSeconds":7200,"MaxWaitTimeInSeconds":10800}' \
  --enable-managed-spot-training \
  --checkpoint-config '{"S3Uri":"s3://my-bucket/checkpoints/"}'

aws sagemaker describe-training-job --training-job-name my-training-job
aws sagemaker list-training-jobs
aws sagemaker list-training-jobs --status-equals InProgress
aws sagemaker list-training-jobs --sort-by CreationTime --sort-order Descending --max-results 10
aws sagemaker stop-training-job --training-job-name my-training-job

# --- Models ---
aws sagemaker create-model \
  --model-name my-model \
  --primary-container '{"Image":"763104351884.dkr.ecr.us-east-1.amazonaws.com/pytorch-inference:2.1.0-cpu-py310-ubuntu20.04-sagemaker","ModelDataUrl":"s3://my-bucket/output/my-training-job/output/model.tar.gz","Environment":{"SAGEMAKER_CONTAINER_LOG_LEVEL":"20","SAGEMAKER_REGION":"us-east-1"}}' \
  --execution-role-arn arn:aws:iam::123456789012:role/SageMakerRole

aws sagemaker describe-model --model-name my-model
aws sagemaker list-models
aws sagemaker delete-model --model-name my-model

# --- Endpoint Configuration ---
aws sagemaker create-endpoint-config \
  --endpoint-config-name my-endpoint-config \
  --production-variants '[{"VariantName":"AllTraffic","ModelName":"my-model","InitialInstanceCount":1,"InstanceType":"ml.m5.large","InitialVariantWeight":1}]'

# Endpoint config with A/B traffic splitting
aws sagemaker create-endpoint-config \
  --endpoint-config-name ab-test-config \
  --production-variants '[{"VariantName":"ModelV1","ModelName":"my-model-v1","InitialInstanceCount":1,"InstanceType":"ml.m5.large","InitialVariantWeight":0.9},{"VariantName":"ModelV2","ModelName":"my-model-v2","InitialInstanceCount":1,"InstanceType":"ml.m5.large","InitialVariantWeight":0.1}]'

# Serverless endpoint config
aws sagemaker create-endpoint-config \
  --endpoint-config-name serverless-config \
  --production-variants '[{"VariantName":"AllTraffic","ModelName":"my-model","ServerlessConfig":{"MemorySizeInMB":2048,"MaxConcurrency":10}}]'

aws sagemaker describe-endpoint-config --endpoint-config-name my-endpoint-config
aws sagemaker delete-endpoint-config --endpoint-config-name my-endpoint-config

# --- Endpoints ---
aws sagemaker create-endpoint \
  --endpoint-name my-endpoint \
  --endpoint-config-name my-endpoint-config

aws sagemaker describe-endpoint --endpoint-name my-endpoint
aws sagemaker list-endpoints
aws sagemaker list-endpoints --status-equals InService
aws sagemaker update-endpoint \
  --endpoint-name my-endpoint \
  --endpoint-config-name new-endpoint-config
aws sagemaker delete-endpoint --endpoint-name my-endpoint

# --- Batch Transform ---
aws sagemaker create-transform-job \
  --transform-job-name my-batch-job \
  --model-name my-model \
  --transform-input '{"DataSource":{"S3DataSource":{"S3DataType":"S3Prefix","S3Uri":"s3://my-bucket/batch-input/"}},"ContentType":"text/csv","SplitType":"Line"}' \
  --transform-output '{"S3OutputPath":"s3://my-bucket/batch-output/","AssembleWith":"Line"}' \
  --transform-resources '{"InstanceType":"ml.m5.large","InstanceCount":1}'

aws sagemaker describe-transform-job --transform-job-name my-batch-job
aws sagemaker list-transform-jobs
aws sagemaker stop-transform-job --transform-job-name my-batch-job

# --- Pipelines ---
aws sagemaker create-pipeline \
  --pipeline-name my-ml-pipeline \
  --pipeline-definition file://pipeline-definition.json \
  --role-arn arn:aws:iam::123456789012:role/SageMakerRole

aws sagemaker start-pipeline-execution \
  --pipeline-name my-ml-pipeline \
  --pipeline-parameters '[{"Name":"TrainingDataS3Uri","Value":"s3://my-bucket/train/"},{"Name":"ModelOutputS3Uri","Value":"s3://my-bucket/model/"}]'

aws sagemaker describe-pipeline-execution --pipeline-execution-arn EXECUTION_ARN
aws sagemaker list-pipeline-executions --pipeline-name my-ml-pipeline
aws sagemaker list-pipeline-execution-steps --pipeline-execution-arn EXECUTION_ARN
aws sagemaker describe-pipeline --pipeline-name my-ml-pipeline
aws sagemaker delete-pipeline --pipeline-name my-ml-pipeline

# --- Feature Store ---
aws sagemaker create-feature-group \
  --feature-group-name customer-features \
  --record-identifier-feature-name customer_id \
  --event-time-feature-name event_time \
  --feature-definitions '[{"FeatureName":"customer_id","FeatureType":"Integral"},{"FeatureName":"event_time","FeatureType":"Fractional"},{"FeatureName":"total_purchases","FeatureType":"Integral"},{"FeatureName":"avg_order_value","FeatureType":"Fractional"},{"FeatureName":"customer_segment","FeatureType":"String"}]' \
  --online-store-config '{"EnableOnlineStore":true}' \
  --offline-store-config '{"S3StorageConfig":{"S3Uri":"s3://my-bucket/feature-store/"},"DisableGlueTableCreation":false}'

aws sagemaker describe-feature-group --feature-group-name customer-features
aws sagemaker list-feature-groups
aws sagemaker delete-feature-group --feature-group-name customer-features

# --- Model Monitor ---
aws sagemaker create-monitoring-schedule \
  --monitoring-schedule-name data-quality-monitor \
  --monitoring-schedule-config '{"MonitoringJobDefinitionName":"my-monitoring-job","MonitoringType":"DataQuality","ScheduleConfig":{"ScheduleExpression":"cron(0 * ? * * *)"}}'

aws sagemaker describe-monitoring-schedule --monitoring-schedule-name data-quality-monitor
aws sagemaker list-monitoring-schedules
aws sagemaker start-monitoring-schedule --monitoring-schedule-name data-quality-monitor
aws sagemaker stop-monitoring-schedule --monitoring-schedule-name data-quality-monitor
aws sagemaker delete-monitoring-schedule --monitoring-schedule-name data-quality-monitor

# --- Hyperparameter Tuning ---
aws sagemaker create-hyper-parameter-tuning-job \
  --hyper-parameter-tuning-job-name my-hpo-job \
  --hyper-parameter-tuning-job-config '{"Strategy":"Bayesian","HyperParameterTuningJobObjective":{"Type":"Maximize","MetricName":"validation:accuracy"},"ResourceLimits":{"MaxNumberOfTrainingJobs":20,"MaxParallelTrainingJobs":4},"ParameterRanges":{"ContinuousParameterRanges":[{"Name":"learning-rate","MinValue":"0.0001","MaxValue":"0.1","ScalingType":"Logarithmic"}],"IntegerParameterRanges":[{"Name":"batch-size","MinValue":"16","MaxValue":"256","ScalingType":"Linear"}]}}' \
  --training-job-definition '{"AlgorithmSpecification":{"TrainingImage":"IMAGE_URI","TrainingInputMode":"File"},"RoleArn":"arn:aws:iam::123456789012:role/SageMakerRole","InputDataConfig":[{"ChannelName":"training","DataSource":{"S3DataSource":{"S3DataType":"S3Prefix","S3Uri":"s3://my-bucket/train/"}}}],"OutputDataConfig":{"S3OutputPath":"s3://my-bucket/hpo-output/"},"ResourceConfig":{"InstanceType":"ml.p3.2xlarge","InstanceCount":1,"VolumeSizeInGB":50},"StoppingCondition":{"MaxRuntimeInSeconds":3600}}'

aws sagemaker describe-hyper-parameter-tuning-job --hyper-parameter-tuning-job-name my-hpo-job
```

---

## Amazon SageMaker Runtime

```bash
# --- Real-time Endpoint Invocation ---
aws sagemaker-runtime invoke-endpoint \
  --endpoint-name my-endpoint \
  --content-type application/json \
  --body '{"inputs":"Classify this review as positive or negative: The product is excellent!"}' \
  output.json
cat output.json

# Invoke with CSV input
aws sagemaker-runtime invoke-endpoint \
  --endpoint-name my-endpoint \
  --content-type text/csv \
  --body "1.5,2.3,0.8,1.2" \
  output.json

# Invoke with specific target variant (A/B test)
aws sagemaker-runtime invoke-endpoint \
  --endpoint-name ab-test-endpoint \
  --content-type application/json \
  --body '{"data":"sample input"}' \
  --target-variant ModelV2 \
  output.json

# --- Async Endpoint Invocation ---
aws sagemaker-runtime invoke-endpoint-async \
  --endpoint-name my-async-endpoint \
  --content-type application/json \
  --input-location s3://my-bucket/async-input/request.json \
  --invocation-timeout-seconds 3600
# Returns an OutputLocation (S3 path) to poll for the result
```
