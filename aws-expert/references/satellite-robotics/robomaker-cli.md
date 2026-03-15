# AWS RoboMaker — CLI Reference

For service concepts, see [robomaker-capabilities.md](robomaker-capabilities.md).

> **Deprecation Note**: Fleet management APIs (robots, fleets, deployment jobs) were deprecated and retired. Only simulation capabilities are shown below. Use AWS IoT Greengrass for physical robot deployment.

---

## Robot Applications

```bash
# --- Create a robot application ---
aws robomaker create-robot-application \
  --name "MyRobot-NavigationApp" \
  --sources '[
    {
      "s3Bucket": "my-robomaker-bundles",
      "s3Key": "robot-apps/navigation-app-v1.2.tar.gz",
      "architecture": "X86_64"
    }
  ]' \
  --robot-software-suite '{
    "name": "ROS2",
    "version": "Humble"
  }' \
  --environment '{
    "uri": "123456789012.dkr.ecr.us-east-1.amazonaws.com/my-robot-app:latest"
  }'

# --- Create a robot application version (immutable snapshot) ---
aws robomaker create-robot-application-version \
  --application arn:aws:robomaker:us-east-1:123456789012:robot-application/MyRobot-NavigationApp/1234567890

# --- List / describe robot applications ---
aws robomaker list-robot-applications
aws robomaker list-robot-applications --version-qualifier "Latest"

aws robomaker describe-robot-application \
  --application arn:aws:robomaker:us-east-1:123456789012:robot-application/MyRobot-NavigationApp/1234567890

# --- Update a robot application ---
aws robomaker update-robot-application \
  --application arn:aws:robomaker:us-east-1:123456789012:robot-application/MyRobot-NavigationApp/1234567890 \
  --sources '[
    {
      "s3Bucket": "my-robomaker-bundles",
      "s3Key": "robot-apps/navigation-app-v1.3.tar.gz",
      "architecture": "X86_64"
    }
  ]' \
  --robot-software-suite '{"name": "ROS2", "version": "Humble"}'

# --- Delete a robot application ---
aws robomaker delete-robot-application \
  --application arn:aws:robomaker:us-east-1:123456789012:robot-application/MyRobot-NavigationApp/1234567890
```

---

## Simulation Applications

```bash
# --- Create a simulation application ---
aws robomaker create-simulation-application \
  --name "WarehouseSimApp" \
  --sources '[
    {
      "s3Bucket": "my-robomaker-bundles",
      "s3Key": "sim-apps/warehouse-world-v2.0.tar.gz",
      "architecture": "X86_64"
    }
  ]' \
  --simulation-software-suite '{
    "name": "Gazebo",
    "version": "11"
  }' \
  --robot-software-suite '{
    "name": "ROS2",
    "version": "Humble"
  }' \
  --rendering-engine '{"name": "OGRE", "version": "1.x"}'

# --- Create a simulation application version ---
aws robomaker create-simulation-application-version \
  --application arn:aws:robomaker:us-east-1:123456789012:simulation-application/WarehouseSimApp/1234567890

# --- List / describe simulation applications ---
aws robomaker list-simulation-applications
aws robomaker describe-simulation-application \
  --application arn:aws:robomaker:us-east-1:123456789012:simulation-application/WarehouseSimApp/1234567890

# --- Update a simulation application ---
aws robomaker update-simulation-application \
  --application arn:aws:robomaker:us-east-1:123456789012:simulation-application/WarehouseSimApp/1234567890 \
  --sources '[{"s3Bucket": "my-robomaker-bundles", "s3Key": "sim-apps/warehouse-world-v2.1.tar.gz", "architecture": "X86_64"}]' \
  --simulation-software-suite '{"name": "Gazebo", "version": "11"}' \
  --robot-software-suite '{"name": "ROS2", "version": "Humble"}'

# --- Delete a simulation application ---
aws robomaker delete-simulation-application \
  --application arn:aws:robomaker:us-east-1:123456789012:simulation-application/WarehouseSimApp/1234567890
```

---

## Simulation Jobs

```bash
# --- Create a simulation job ---
aws robomaker create-simulation-job \
  --iam-role "arn:aws:iam::123456789012:role/RoboMakerSimulationRole" \
  --max-job-duration-in-seconds 3600 \
  --failure-behavior Continue \
  --robot-applications '[
    {
      "application": "arn:aws:robomaker:us-east-1:123456789012:robot-application/MyRobot-NavigationApp/1234567890",
      "launchConfig": {
        "packageName": "navigation",
        "launchFile": "navigate_to_goal.launch.py",
        "environmentVariables": {
          "ROBOT_ENV": "simulation",
          "LOG_LEVEL": "INFO"
        }
      },
      "uploadConfigurations": [
        {
          "name": "NavLogs",
          "path": "/home/user/.ros/log/",
          "uploadBehavior": "UPLOAD_ON_TERMINATE"
        }
      ]
    }
  ]' \
  --simulation-applications '[
    {
      "application": "arn:aws:robomaker:us-east-1:123456789012:simulation-application/WarehouseSimApp/1234567890",
      "launchConfig": {
        "packageName": "warehouse_world",
        "launchFile": "warehouse.launch.py",
        "environmentVariables": {
          "WORLD_SEED": "42"
        }
      },
      "worldConfigs": [
        {
          "world": "arn:aws:robomaker:us-east-1:123456789012:world/MyWorld/1234567890"
        }
      ]
    }
  ]' \
  --output-location '{"s3Bucket": "my-sim-results", "s3Prefix": "navigation-tests/run-001"}' \
  --logging-config '{"recordAllRosTopics": false}' \
  --compute '{"simulationUnitLimit": 5, "gpuUnitLimit": 0, "computeType": "CPU"}' \
  --tags '{"TestRun": "NavigationSuite-001", "Environment": "Warehouse"}'

# --- Describe a simulation job ---
aws robomaker describe-simulation-job \
  --job arn:aws:robomaker:us-east-1:123456789012:simulation-job/SimJob-a1b2c3d4e5f67890

# --- List simulation jobs ---
aws robomaker list-simulation-jobs

aws robomaker list-simulation-jobs \
  --filters '[{"name": "status", "values": ["Running"]}]'

# --- Restart a simulation job ---
aws robomaker restart-simulation-job \
  --job arn:aws:robomaker:us-east-1:123456789012:simulation-job/SimJob-a1b2c3d4e5f67890

# --- Cancel a simulation job ---
aws robomaker cancel-simulation-job \
  --job arn:aws:robomaker:us-east-1:123456789012:simulation-job/SimJob-a1b2c3d4e5f67890

# --- Batch describe simulation jobs ---
aws robomaker batch-describe-simulation-job \
  --jobs '[
    "arn:aws:robomaker:us-east-1:123456789012:simulation-job/SimJob-aaa",
    "arn:aws:robomaker:us-east-1:123456789012:simulation-job/SimJob-bbb"
  ]'
```

---

## Simulation Job Batches

```bash
# --- Start a simulation job batch (parallel parameter sweep) ---
aws robomaker start-simulation-job-batch \
  --batch-policy '{
    "timeoutInSeconds": 7200,
    "maxConcurrency": 10
  }' \
  --create-simulation-job-requests '[
    {
      "maxJobDurationInSeconds": 1800,
      "iamRole": "arn:aws:iam::123456789012:role/RoboMakerSimulationRole",
      "robotApplications": [{"application": "arn:...robot-app/...", "launchConfig": {"packageName": "nav", "launchFile": "nav.launch.py"}}],
      "simulationApplications": [{"application": "arn:...sim-app/...", "launchConfig": {"packageName": "world", "launchFile": "world.launch.py"}}],
      "tags": {"Scenario": "Scenario-001"}
    },
    {
      "maxJobDurationInSeconds": 1800,
      "iamRole": "arn:aws:iam::123456789012:role/RoboMakerSimulationRole",
      "robotApplications": [{"application": "arn:...robot-app/...", "launchConfig": {"packageName": "nav", "launchFile": "nav.launch.py"}}],
      "simulationApplications": [{"application": "arn:...sim-app/...", "launchConfig": {"packageName": "world", "launchFile": "world.launch.py"}}],
      "tags": {"Scenario": "Scenario-002"}
    }
  ]' \
  --tags '{"BatchName": "NavigationTest-Batch-2024-03-15"}'

aws robomaker describe-simulation-job-batch \
  --batch arn:aws:robomaker:us-east-1:123456789012:simulation-job-batch/Batch-a1b2c3d4

aws robomaker list-simulation-job-batches
aws robomaker cancel-simulation-job-batch \
  --batch arn:aws:robomaker:us-east-1:123456789012:simulation-job-batch/Batch-a1b2c3d4
```

---

## WorldForge — World Templates

```bash
# --- Create a world template ---
aws robomaker create-world-template \
  --name "OfficeFloorplan" \
  --template-body file://office-world-template.json

# --- List / describe world templates ---
aws robomaker list-world-templates

aws robomaker describe-world-template \
  --template arn:aws:robomaker:us-east-1:123456789012:world-template/MyWorldTemplate/1234567890

# Get the template body (JSON definition)
aws robomaker get-world-template-body \
  --template arn:aws:robomaker:us-east-1:123456789012:world-template/MyWorldTemplate/1234567890

# --- Update a world template ---
aws robomaker update-world-template \
  --template arn:aws:robomaker:us-east-1:123456789012:world-template/MyWorldTemplate/1234567890 \
  --name "OfficeFloorplan-v2" \
  --template-body file://office-world-template-v2.json

# --- Delete a world template ---
aws robomaker delete-world-template \
  --template arn:aws:robomaker:us-east-1:123456789012:world-template/MyWorldTemplate/1234567890
```

---

## WorldForge — World Generation Jobs

```bash
# --- Create a world generation job ---
aws robomaker create-world-generation-job \
  --template arn:aws:robomaker:us-east-1:123456789012:world-template/MyWorldTemplate/1234567890 \
  --world-count '{
    "floorplanCount": 20,
    "interiorCountPerFloorplan": 3
  }' \
  --iam-role "arn:aws:iam::123456789012:role/RoboMakerWorldGenRole" \
  --tags '{"Campaign": "Navigation-TestGen-Q1-2024"}'

# --- Describe a world generation job ---
aws robomaker describe-world-generation-job \
  --job arn:aws:robomaker:us-east-1:123456789012:world-generation-job/WorldGenJob-a1b2c3d4

aws robomaker list-world-generation-jobs
aws robomaker list-world-generation-jobs \
  --filters '[{"name": "templateId", "values": ["MyWorldTemplate"]}]'

aws robomaker cancel-world-generation-job \
  --job arn:aws:robomaker:us-east-1:123456789012:world-generation-job/WorldGenJob-a1b2c3d4
```

---

## WorldForge — Worlds

```bash
# --- List generated worlds ---
aws robomaker list-worlds

aws robomaker list-worlds \
  --filters '[{"name": "templateId", "values": ["MyWorldTemplate"]}]'

aws robomaker describe-world \
  --world arn:aws:robomaker:us-east-1:123456789012:world/MyWorld/1234567890

aws robomaker delete-world \
  --worlds '[
    "arn:aws:robomaker:us-east-1:123456789012:world/MyWorld/aaaa",
    "arn:aws:robomaker:us-east-1:123456789012:world/MyWorld/bbbb"
  ]'
```

---

## WorldForge — World Export Jobs

```bash
# --- Create a world export job (export worlds to S3 for reuse) ---
aws robomaker create-world-export-job \
  --worlds '[
    "arn:aws:robomaker:us-east-1:123456789012:world/MyWorld/1234567890",
    "arn:aws:robomaker:us-east-1:123456789012:world/MyWorld/0987654321"
  ]' \
  --iam-role "arn:aws:iam::123456789012:role/RoboMakerWorldExportRole" \
  --output-location '{
    "s3Bucket": "my-world-exports",
    "s3Prefix": "exports/2024-03-15/"
  }'

aws robomaker describe-world-export-job \
  --job arn:aws:robomaker:us-east-1:123456789012:world-export-job/WorldExportJob-a1b2c3d4

aws robomaker list-world-export-jobs
aws robomaker cancel-world-export-job \
  --job arn:aws:robomaker:us-east-1:123456789012:world-export-job/WorldExportJob-a1b2c3d4
```

---

## Tags

```bash
# --- List tags for a resource ---
aws robomaker list-tags-for-resource \
  --resource-arn "arn:aws:robomaker:us-east-1:123456789012:simulation-job/SimJob-a1b2c3d4e5f67890"

# --- Tag a resource ---
aws robomaker tag-resource \
  --resource-arn "arn:aws:robomaker:us-east-1:123456789012:simulation-job/SimJob-a1b2c3d4e5f67890" \
  --tags '{"Project": "NavigationTest", "Environment": "CI"}'

# --- Untag a resource ---
aws robomaker untag-resource \
  --resource-arn "arn:aws:robomaker:us-east-1:123456789012:simulation-job/SimJob-a1b2c3d4e5f67890" \
  --tag-keys '["Project"]'
```
