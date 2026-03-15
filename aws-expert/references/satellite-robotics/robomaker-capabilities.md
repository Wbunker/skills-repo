# AWS RoboMaker — Capabilities Reference

For CLI commands, see [robomaker-cli.md](robomaker-cli.md).

---

## AWS RoboMaker

**Purpose**: Cloud-based service for developing, simulating, and deploying robotic applications at scale. Built on the Robot Operating System (ROS/ROS2) ecosystem.

> **Important deprecation notice**: AWS RoboMaker fleet management (robot deployment) APIs were **deprecated in September 2022** for new customers and the existing fleet management feature was **retired** for all customers after **January 31, 2025**. AWS recommends using **AWS IoT Greengrass** for deploying and managing robot software on physical robots. Simulation capabilities (simulation jobs, WorldForge) remain active.

### Core Concepts

| Concept | Description |
|---|---|
| **Robot Application** | Your robot's software packaged as a bundle (compressed .tar archive) for ROS or ROS2; includes compiled nodes, launch files, and configuration. |
| **Simulation Application** | The simulation environment software (e.g., Gazebo world + models); also packaged as a bundle. Describes the virtual world the robot operates in. |
| **Simulation Job** | A single execution of a robot application and simulation application together. Runs on managed compute; generates logs, rosbag recordings, and output files. |
| **Simulation Job Batch** | Run multiple simulation jobs in parallel (parameter sweeps, scenario testing) |
| **World** | A generated or custom simulation environment (floor plans, furniture, obstacles). |
| **WorldForge** | A tool within RoboMaker that automatically generates diverse simulation worlds from templates (floor plans + feature configurations). |
| **World Generation Job** | A job that uses WorldForge to generate multiple world variants from a template in batch. |
| **World Export Job** | Exports generated worlds to S3 as standalone assets for use outside RoboMaker. |

---

## Robot Applications

- Bundles must be uploaded to S3; RoboMaker pulls from S3 at simulation start
- Support **ROS Kinetic, ROS Melodic, ROS2 Foxy, ROS2 Humble**
- Environment variables configurable per simulation job
- Application versions tracked; simulations reference a specific version ARN

---

## Simulation Applications

- Typically includes a **Gazebo** world definition, robot URDF model, and physics configuration
- Packaged separately from the robot application to allow reuse of environments across multiple robot apps
- Rendering mode: **GPU-based** (for visual rendering, computer vision testing) or **CPU-based** (physics-only, faster/cheaper)

---

## Simulation Jobs

### Configuration

| Parameter | Description |
|---|---|
| **Robot application** | ARN of the robot application version to run |
| **Simulation application** | ARN of the simulation application version to run |
| **IAM role** | Role assumed by the simulation job for S3 access, CloudWatch publishing |
| **Max job duration** | Maximum wall-clock seconds before automatic termination |
| **Output location** | S3 bucket/prefix for logs, rosbag recordings, and output files |
| **Failure behavior** | `Fail` (stop on error) or `Continue` (attempt restart) |
| **Compute configuration** | `CPU` or `GPU` instance; simulation unit count (parallelism within job) |
| **VPC config** | Optional VPC networking for simulation job compute (access private resources) |

### Simulation Job States

`Pending` → `Preparing` → `Running` → `Restarting` → `Completed` / `Failed` / `Cancelled` / `Terminated`

---

## WorldForge

WorldForge automatically generates diverse simulation environments for testing robot behaviors across varied physical layouts.

### Workflow

1. Create a **world template** (defines room types, counts, furniture density)
2. Submit a **world generation job** specifying the template and world count
3. RoboMaker generates N distinct world variants, stores them as world resources
4. Reference generated worlds in simulation jobs for automated scenario testing
5. Optionally **export worlds** to S3 as reusable `.tar.gz` archives

### World Templates

- Define building floor plan characteristics
- Configure interior features: room count, furniture density, lighting
- Generation produces unique world variants meeting the template constraints

---

## Development Environments

RoboMaker provides managed development environments based on **AWS Cloud9**:
- Pre-configured with ROS, Gazebo, and AWS SDK
- Integrated terminal, file editor, and simulation preview
- Deprecated alongside fleet management for new development workflows; AWS now recommends local dev + AWS cloud simulation via CLI/SDK

---

## Replacement: IoT Greengrass for Robot Deployment

For physical robot deployment (replacing the deprecated fleet management):

| Capability | RoboMaker (deprecated) | IoT Greengrass (recommended) |
|---|---|---|
| Software deployment to robots | Fleet management + deployment jobs | Greengrass components + deployments |
| Over-the-air updates | RoboMaker deployment service | IoT Jobs + Greengrass |
| Device management | RoboMaker robot registry | IoT Device Registry (Things) |
| Certificate management | RoboMaker-managed | IoT Core certificates |

---

## Integration Patterns

| Pattern | Description |
|---|---|
| **RoboMaker + S3** | Store robot and simulation bundles in S3; simulation job outputs (logs, rosbags) written back to S3 |
| **RoboMaker + CloudWatch** | Publish simulation metrics and logs; set alarms on test failure rates |
| **RoboMaker + Step Functions** | Orchestrate simulation job batch workflows; trigger downstream analysis when jobs complete |

---

## Use Cases

- Testing robot software with simulated worlds across diverse generated environments
- Regression testing against a matrix of world configurations (WorldForge)
- Parallel simulations via simulation job batches for parameter sweeps
- CI/CD integration: automated simulation runs triggered by code changes
