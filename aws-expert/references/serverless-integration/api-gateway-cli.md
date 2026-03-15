# AWS API Gateway — CLI Reference
For service concepts, see [api-gateway-capabilities.md](api-gateway-capabilities.md).

## API Gateway (REST) — apigateway

```bash
# --- Create REST API ---
aws apigateway create-rest-api \
  --name MyAPI \
  --description "Production REST API" \
  --endpoint-configuration types=REGIONAL

aws apigateway get-rest-apis
aws apigateway delete-rest-api --rest-api-id abc123

# --- Resources and methods ---
# Get root resource ID
ROOT_ID=$(aws apigateway get-resources --rest-api-id abc123 \
  --query 'items[?path==`/`].id' --output text)

# Create resource /users
aws apigateway create-resource \
  --rest-api-id abc123 \
  --parent-id $ROOT_ID \
  --path-part users

# Create method GET /users
aws apigateway put-method \
  --rest-api-id abc123 \
  --resource-id RESOURCE_ID \
  --http-method GET \
  --authorization-type NONE

# Method with Cognito authorizer
aws apigateway put-method \
  --rest-api-id abc123 \
  --resource-id RESOURCE_ID \
  --http-method POST \
  --authorization-type COGNITO_USER_POOLS \
  --authorizer-id AUTH_ID

# --- Integrations ---
# Lambda proxy integration
aws apigateway put-integration \
  --rest-api-id abc123 \
  --resource-id RESOURCE_ID \
  --http-method GET \
  --type AWS_PROXY \
  --integration-http-method POST \
  --uri "arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:123456789012:function:my-function/invocations"

# AWS service integration (SQS)
aws apigateway put-integration \
  --rest-api-id abc123 \
  --resource-id RESOURCE_ID \
  --http-method POST \
  --type AWS \
  --integration-http-method POST \
  --uri "arn:aws:apigateway:us-east-1:sqs:path/123456789012/my-queue" \
  --credentials arn:aws:iam::123456789012:role/apigw-sqs-role \
  --request-parameters '{"integration.request.header.Content-Type":"'"'"'application/x-www-form-urlencoded'"'"'"}'

# Mock integration
aws apigateway put-integration \
  --rest-api-id abc123 \
  --resource-id RESOURCE_ID \
  --http-method OPTIONS \
  --type MOCK \
  --request-templates '{"application/json":"{\"statusCode\":200}"}'

# Method response
aws apigateway put-method-response \
  --rest-api-id abc123 \
  --resource-id RESOURCE_ID \
  --http-method GET \
  --status-code 200

# Integration response
aws apigateway put-integration-response \
  --rest-api-id abc123 \
  --resource-id RESOURCE_ID \
  --http-method GET \
  --status-code 200 \
  --selection-pattern ""

# --- Authorizers ---
aws apigateway create-authorizer \
  --rest-api-id abc123 \
  --name CognitoAuthorizer \
  --type COGNITO_USER_POOLS \
  --provider-arns arn:aws:cognito-idp:us-east-1:123456789012:userpool/us-east-1_abc123 \
  --identity-source method.request.header.Authorization

# Lambda TOKEN authorizer
aws apigateway create-authorizer \
  --rest-api-id abc123 \
  --name LambdaTokenAuth \
  --type TOKEN \
  --authorizer-uri "arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:123456789012:function:my-authorizer/invocations" \
  --identity-source method.request.header.Authorization \
  --authorizer-result-ttl-in-seconds 300

# Lambda REQUEST authorizer
aws apigateway create-authorizer \
  --rest-api-id abc123 \
  --name LambdaRequestAuth \
  --type REQUEST \
  --authorizer-uri "arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:123456789012:function:request-authorizer/invocations" \
  --identity-source "method.request.header.X-Api-Key,method.request.querystring.clientId"

# --- Deployments and stages ---
aws apigateway create-deployment \
  --rest-api-id abc123 \
  --stage-name prod \
  --description "Production deployment v1.2"

aws apigateway create-stage \
  --rest-api-id abc123 \
  --stage-name staging \
  --deployment-id DEPLOYMENT_ID

# Enable stage-level throttling and caching
aws apigateway update-stage \
  --rest-api-id abc123 \
  --stage-name prod \
  --patch-operations \
    op=replace,path=/defaultRouteSettings/throttlingRateLimit,value=1000 \
    op=replace,path=/defaultRouteSettings/throttlingBurstLimit,value=2000 \
    op=replace,path=/cacheClusterEnabled,value=true \
    op=replace,path=/cacheClusterSize,value=0.5

# Enable access logging
aws apigateway update-stage \
  --rest-api-id abc123 \
  --stage-name prod \
  --patch-operations \
    op=replace,path=/accessLogSettings/destinationArn,value=arn:aws:logs:us-east-1:123456789012:log-group:/apigw/prod

# --- Usage plans and API keys ---
aws apigateway create-api-key \
  --name MyAPIKey \
  --enabled

aws apigateway create-usage-plan \
  --name StandardPlan \
  --throttle burstLimit=100,rateLimit=50 \
  --quota limit=10000,offset=0,period=MONTH \
  --api-stages '[{"apiId":"abc123","stage":"prod"}]'

aws apigateway create-usage-plan-key \
  --usage-plan-id PLAN_ID \
  --key-id KEY_ID \
  --key-type API_KEY

aws apigateway get-usage-plans
aws apigateway get-api-keys --include-values
```

---

## API Gateway V2 (HTTP + WebSocket) — apigatewayv2

```bash
# --- HTTP API ---
# Create HTTP API with Lambda proxy (quick create)
aws apigatewayv2 create-api \
  --name MyHTTPAPI \
  --protocol-type HTTP \
  --target arn:aws:lambda:us-east-1:123456789012:function:my-function

# Create HTTP API manually
aws apigatewayv2 create-api \
  --name MyHTTPAPI \
  --protocol-type HTTP \
  --cors-configuration \
    AllowOrigins="https://example.com",AllowMethods="GET,POST",AllowHeaders="Content-Type"

# Create integration
aws apigatewayv2 create-integration \
  --api-id API_ID \
  --integration-type AWS_PROXY \
  --integration-uri arn:aws:lambda:us-east-1:123456789012:function:my-function \
  --payload-format-version 2.0

# Create route
aws apigatewayv2 create-route \
  --api-id API_ID \
  --route-key "GET /users" \
  --target integrations/INTEGRATION_ID

# Update route with authorizer
aws apigatewayv2 update-route \
  --api-id API_ID \
  --route-id ROUTE_ID \
  --authorization-type JWT \
  --authorizer-id AUTH_ID

# JWT authorizer
aws apigatewayv2 create-authorizer \
  --api-id API_ID \
  --authorizer-type JWT \
  --name JWTAuth \
  --identity-source '$request.header.Authorization' \
  --jwt-configuration Audience="my-app-client-id",Issuer="https://cognito-idp.us-east-1.amazonaws.com/us-east-1_abc123"

# Lambda REQUEST authorizer
aws apigatewayv2 create-authorizer \
  --api-id API_ID \
  --authorizer-type REQUEST \
  --name LambdaAuth \
  --authorizer-uri "arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:123456789012:function:my-auth/invocations" \
  --authorizer-payload-format-version 2.0 \
  --enable-simple-responses \
  --identity-source '$request.header.Authorization'

# Stage and deployment
aws apigatewayv2 create-stage \
  --api-id API_ID \
  --stage-name prod \
  --auto-deploy

aws apigatewayv2 create-deployment \
  --api-id API_ID \
  --stage-name prod

# Custom domain
aws apigatewayv2 create-domain-name \
  --domain-name api.example.com \
  --domain-name-configurations \
    CertificateArn=arn:aws:acm:us-east-1:123456789012:certificate/CERT_ID,EndpointType=REGIONAL

aws apigatewayv2 create-api-mapping \
  --domain-name api.example.com \
  --api-id API_ID \
  --stage prod

aws apigatewayv2 get-apis
aws apigatewayv2 delete-api --api-id API_ID

# --- WebSocket API ---
aws apigatewayv2 create-api \
  --name MyWebSocketAPI \
  --protocol-type WEBSOCKET \
  --route-selection-expression '$request.body.action'

# $connect route
aws apigatewayv2 create-route \
  --api-id WS_API_ID \
  --route-key '$connect' \
  --target integrations/CONNECT_INTEGRATION_ID

# $disconnect route
aws apigatewayv2 create-route \
  --api-id WS_API_ID \
  --route-key '$disconnect' \
  --target integrations/DISCONNECT_INTEGRATION_ID

# $default route
aws apigatewayv2 create-route \
  --api-id WS_API_ID \
  --route-key '$default' \
  --target integrations/DEFAULT_INTEGRATION_ID

# Custom route
aws apigatewayv2 create-route \
  --api-id WS_API_ID \
  --route-key 'sendMessage' \
  --target integrations/SEND_INTEGRATION_ID
```
