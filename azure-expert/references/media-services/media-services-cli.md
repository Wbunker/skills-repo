# Azure Media Services — CLI Reference
For service concepts, see [media-services-capabilities.md](media-services-capabilities.md).

> **Note**: Azure Media Services encoding and live streaming are being retired (2024–2025). These commands remain valid for existing deployments. New projects should evaluate FFmpeg, third-party encoders, and Azure AI Video Indexer.

## Media Services Account Management

```bash
# --- Account ---
az ams account create \
  --resource-group myRG \
  --name myMediaAccount \
  --storage-account myStorageAccount \
  --location eastus                             # Create AMS account linked to storage

az ams account list --resource-group myRG      # List AMS accounts
az ams account show --resource-group myRG --name myMediaAccount  # Show account details

az ams account storage add \
  --resource-group myRG \
  --account-name myMediaAccount \
  --storage-account secondaryStorage            # Add secondary storage account

az ams account delete \
  --resource-group myRG \
  --name myMediaAccount --yes                   # Delete AMS account

# Show managed identity
az ams account show \
  --resource-group myRG \
  --name myMediaAccount \
  --query identity
```

## Assets

```bash
# --- Assets ---
az ams asset create \
  --resource-group myRG \
  --account-name myMediaAccount \
  --name input-video-asset \
  --description "Source video for encoding"    # Create an asset

az ams asset create \
  --resource-group myRG \
  --account-name myMediaAccount \
  --name output-encoded-asset \
  --storage-account myStorageAccount           # Create output asset on specific storage

az ams asset list \
  --resource-group myRG \
  --account-name myMediaAccount               # List all assets

az ams asset show \
  --resource-group myRG \
  --account-name myMediaAccount \
  --name input-video-asset                    # Show asset details (incl. container name)

# Get SAS URL to upload video to asset container
az ams asset get-sas-urls \
  --resource-group myRG \
  --account-name myMediaAccount \
  --name input-video-asset \
  --permissions ReadWrite \
  --expiry-time "2025-12-31T00:00:00Z"        # Get SAS for upload

az ams asset delete \
  --resource-group myRG \
  --account-name myMediaAccount \
  --name output-encoded-asset                 # Delete asset (does not delete storage)
```

## Transforms and Jobs

```bash
# --- Transforms ---
# Create transform with built-in adaptive streaming preset
az ams transform create \
  --resource-group myRG \
  --account-name myMediaAccount \
  --name adaptive-streaming-transform \
  --preset AdaptiveStreaming \
  --description "Multi-bitrate H.264 adaptive streaming"

# Create transform with H.265 preset
az ams transform create \
  --resource-group myRG \
  --account-name myMediaAccount \
  --name hevc-transform \
  --preset H265AdaptiveStreaming

# Create transform with content-aware encoding (best quality/bitrate ratio)
az ams transform create \
  --resource-group myRG \
  --account-name myMediaAccount \
  --name cae-transform \
  --preset ContentAwareEncoding

az ams transform list \
  --resource-group myRG \
  --account-name myMediaAccount               # List transforms

az ams transform show \
  --resource-group myRG \
  --account-name myMediaAccount \
  --name adaptive-streaming-transform         # Show transform details

az ams transform delete \
  --resource-group myRG \
  --account-name myMediaAccount \
  --name old-transform                        # Delete transform

# --- Jobs ---
az ams job create \
  --resource-group myRG \
  --account-name myMediaAccount \
  --transform-name adaptive-streaming-transform \
  --name encode-job-001 \
  --input-asset-name input-video-asset \
  --output-assets assetname=output-encoded-asset  # Submit encoding job

az ams job list \
  --resource-group myRG \
  --account-name myMediaAccount \
  --transform-name adaptive-streaming-transform   # List jobs for a transform

az ams job show \
  --resource-group myRG \
  --account-name myMediaAccount \
  --transform-name adaptive-streaming-transform \
  --name encode-job-001                        # Show job status and progress

az ams job cancel \
  --resource-group myRG \
  --account-name myMediaAccount \
  --transform-name adaptive-streaming-transform \
  --name encode-job-001                        # Cancel a running job

az ams job delete \
  --resource-group myRG \
  --account-name myMediaAccount \
  --transform-name adaptive-streaming-transform \
  --name encode-job-001                        # Delete completed job record
```

## Streaming

```bash
# --- Streaming Endpoints ---
az ams streaming-endpoint list \
  --resource-group myRG \
  --account-name myMediaAccount               # List streaming endpoints

az ams streaming-endpoint show \
  --resource-group myRG \
  --account-name myMediaAccount \
  --name default                              # Show default endpoint

az ams streaming-endpoint start \
  --resource-group myRG \
  --account-name myMediaAccount \
  --name default                              # Start default streaming endpoint

az ams streaming-endpoint stop \
  --resource-group myRG \
  --account-name myMediaAccount \
  --name default                              # Stop endpoint (avoid billing when not needed)

az ams streaming-endpoint create \
  --resource-group myRG \
  --account-name myMediaAccount \
  --name premium-endpoint \
  --scale-units 1 \
  --cdn-enabled true \
  --cdn-provider AkamaiPremiumVerizon         # Create premium streaming endpoint with CDN

# --- Streaming Locators (generate playback URLs) ---
az ams streaming-locator create \
  --resource-group myRG \
  --account-name myMediaAccount \
  --name vod-locator-001 \
  --asset-name output-encoded-asset \
  --streaming-policy-name Predefined_ClearStreamingOnly  # Create clear (unencrypted) locator

az ams streaming-locator create \
  --resource-group myRG \
  --account-name myMediaAccount \
  --name drm-locator-001 \
  --asset-name output-encoded-asset \
  --streaming-policy-name Predefined_MultiDrmCencStreaming \
  --content-key-policy-name myDRMPolicy        # Create DRM-protected locator

az ams streaming-locator get-paths \
  --resource-group myRG \
  --account-name myMediaAccount \
  --name vod-locator-001                       # Get HLS, DASH, and Smooth Streaming URLs

az ams streaming-locator list \
  --resource-group myRG \
  --account-name myMediaAccount               # List all locators

az ams streaming-locator delete \
  --resource-group myRG \
  --account-name myMediaAccount \
  --name vod-locator-001                      # Revoke access by deleting locator
```

## Content Protection

```bash
# --- Content Key Policies (DRM) ---
az ams content-key-policy create \
  --resource-group myRG \
  --account-name myMediaAccount \
  --name myDRMPolicy \
  --description "Multi-DRM policy with JWT token" \
  --policy-option-name playready-option \
  --playready-template '{"AllowTestDevices": false, "ContentKeyLocation": {"OdataType": "#Microsoft.Media.ContentKeyPolicyPlayReadyContentEncryptionKeyFromHeader"}, ...}'  # Create PlayReady policy

az ams content-key-policy list \
  --resource-group myRG \
  --account-name myMediaAccount               # List content key policies

az ams content-key-policy show \
  --resource-group myRG \
  --account-name myMediaAccount \
  --name myDRMPolicy                          # Show policy details

az ams content-key-policy delete \
  --resource-group myRG \
  --account-name myMediaAccount \
  --name myDRMPolicy                          # Delete policy
```

## Live Streaming

```bash
# --- Live Events ---
az ams live-event create \
  --resource-group myRG \
  --account-name myMediaAccount \
  --name myLiveEvent \
  --streaming-protocol RTMP \
  --sku name=Standard \
  --encoding-type None \
  --description "Pass-through live event"     # Create pass-through live event

az ams live-event create \
  --resource-group myRG \
  --account-name myMediaAccount \
  --name myEncodedLiveEvent \
  --streaming-protocol RTMP \
  --sku name=Standard \
  --encoding-type Standard \
  --preset-name Default720p                   # Create live encoding event (720p)

az ams live-event start \
  --resource-group myRG \
  --account-name myMediaAccount \
  --name myLiveEvent                          # Start live event

az ams live-event show \
  --resource-group myRG \
  --account-name myMediaAccount \
  --name myLiveEvent \
  --query properties.input                    # Get RTMP ingest URL

az ams live-event stop \
  --resource-group myRG \
  --account-name myMediaAccount \
  --name myLiveEvent                          # Stop live event

az ams live-event delete \
  --resource-group myRG \
  --account-name myMediaAccount \
  --name myLiveEvent                          # Delete live event

# --- Live Outputs (DVR recording) ---
az ams live-output create \
  --resource-group myRG \
  --account-name myMediaAccount \
  --live-event-name myLiveEvent \
  --name myLiveOutput \
  --asset-name live-recording-asset \
  --archive-window-length PT8H               # Record with 8-hour DVR window

az ams live-output list \
  --resource-group myRG \
  --account-name myMediaAccount \
  --live-event-name myLiveEvent              # List live outputs

az ams live-output delete \
  --resource-group myRG \
  --account-name myMediaAccount \
  --live-event-name myLiveEvent \
  --name myLiveOutput                        # Delete live output (stops recording)
```

## Azure AI Video Indexer

```bash
# Install Video Indexer extension
az extension add --name videoindexer

# --- Account Management ---
az videoindexer account create \
  --resource-group myRG \
  --location eastus \
  --name myVideoIndexer                      # Create Video Indexer account (ARM-integrated)

az videoindexer account list \
  --resource-group myRG                      # List Video Indexer accounts

az videoindexer account show \
  --resource-group myRG \
  --name myVideoIndexer                      # Show account details

az videoindexer account delete \
  --resource-group myRG \
  --name myVideoIndexer --yes                # Delete account

# Get access token for REST API calls
az videoindexer account generate-access-token \
  --resource-group myRG \
  --name myVideoIndexer \
  --scope Account \
  --permission-type Contributor              # Generate API access token
```
