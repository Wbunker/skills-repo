# AWS Elastic Beanstalk — CLI Reference

For service concepts, see [elastic-beanstalk-capabilities.md](elastic-beanstalk-capabilities.md).

## Elastic Beanstalk

```bash
# --- Applications ---
aws elasticbeanstalk create-application \
  --application-name my-web-app \
  --description "My production web application"

aws elasticbeanstalk describe-applications
aws elasticbeanstalk update-application \
  --application-name my-web-app \
  --description "Updated description"
aws elasticbeanstalk delete-application \
  --application-name my-web-app \
  --terminate-env-by-force

# --- Application Versions ---
# Create a version from an S3 artifact
aws elasticbeanstalk create-application-version \
  --application-name my-web-app \
  --version-label v1.2.0 \
  --description "Feature release 1.2.0" \
  --source-bundle '{"S3Bucket":"my-eb-artifacts","S3Key":"my-web-app/v1.2.0.zip"}' \
  --auto-create-application

aws elasticbeanstalk describe-application-versions \
  --application-name my-web-app

aws elasticbeanstalk delete-application-version \
  --application-name my-web-app \
  --version-label v1.0.0 \
  --delete-source-bundle

# --- Environments ---
# Create a web server environment
aws elasticbeanstalk create-environment \
  --application-name my-web-app \
  --environment-name my-web-app-prod \
  --solution-stack-name "64bit Amazon Linux 2023 v4.0.0 running Python 3.11" \
  --version-label v1.2.0 \
  --option-settings \
    "Namespace=aws:autoscaling:asg,OptionName=MinSize,Value=2" \
    "Namespace=aws:autoscaling:asg,OptionName=MaxSize,Value=10" \
    "Namespace=aws:ec2:instances,OptionName=InstanceTypes,Value=m7g.large" \
    "Namespace=aws:elbv2:loadbalancer,OptionName=IdleTimeout,Value=60" \
    "Namespace=aws:elasticbeanstalk:environment,OptionName=EnvironmentType,Value=LoadBalanced" \
    "Namespace=aws:elasticbeanstalk:application:environment,OptionName=LOG_LEVEL,Value=INFO"

aws elasticbeanstalk describe-environments
aws elasticbeanstalk describe-environments --application-name my-web-app
aws elasticbeanstalk describe-environment-resources --environment-name my-web-app-prod
aws elasticbeanstalk describe-environment-health \
  --environment-name my-web-app-prod \
  --attribute-names All

aws elasticbeanstalk describe-instances-health \
  --environment-name my-web-app-prod \
  --attribute-names All

# --- Deploy a New Version ---
aws elasticbeanstalk update-environment \
  --application-name my-web-app \
  --environment-name my-web-app-prod \
  --version-label v1.3.0

# Update environment configuration (change instance type, add option)
aws elasticbeanstalk update-environment \
  --application-name my-web-app \
  --environment-name my-web-app-prod \
  --option-settings "Namespace=aws:ec2:instances,OptionName=InstanceTypes,Value=m7g.xlarge"

# Abort an in-progress update
aws elasticbeanstalk abort-environment-update --environment-name my-web-app-prod

# --- Blue/Green Deployment (CNAME Swap) ---
aws elasticbeanstalk swap-environment-cnames \
  --source-environment-name my-web-app-prod \
  --destination-environment-name my-web-app-staging

# --- Managed Actions (Platform Updates) ---
aws elasticbeanstalk describe-environment-managed-actions \
  --environment-name my-web-app-prod

aws elasticbeanstalk apply-environment-managed-action \
  --environment-name my-web-app-prod \
  --action-id "Platform Update" \
  --action-type InstanceRefresh

# --- Configuration Templates ---
aws elasticbeanstalk create-configuration-template \
  --application-name my-web-app \
  --template-name production-config \
  --solution-stack-name "64bit Amazon Linux 2023 v4.0.0 running Python 3.11" \
  --option-settings \
    "Namespace=aws:autoscaling:asg,OptionName=MinSize,Value=2" \
    "Namespace=aws:autoscaling:asg,OptionName=MaxSize,Value=10"

aws elasticbeanstalk describe-configuration-settings \
  --application-name my-web-app \
  --environment-name my-web-app-prod

# --- Platform Versions ---
aws elasticbeanstalk list-available-solution-stacks
aws elasticbeanstalk list-platform-versions \
  --filters "Type=ProgrammingLanguage,Operator=contains,Values=Python"
aws elasticbeanstalk list-platform-branches

# --- Events ---
aws elasticbeanstalk describe-events \
  --environment-name my-web-app-prod \
  --severity ERROR

# --- Terminate Environment ---
aws elasticbeanstalk terminate-environment \
  --environment-name my-web-app-staging \
  --terminate-resources

# Rebuild environment from scratch
aws elasticbeanstalk rebuild-environment --environment-name my-web-app-prod
```
