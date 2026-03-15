# AWS Cloud IDE & Shell — Capabilities Reference

For CLI commands, see [cloud-ide-shell-cli.md](cloud-ide-shell-cli.md).

---

## AWS Cloud9

**Purpose**: Browser-based integrated development environment (IDE) for writing, running, and debugging code directly in the browser, with a pre-authenticated AWS CLI and terminal access to the underlying EC2 instance.

> **Deprecation Note**: As of July 2023, AWS Cloud9 is no longer available to new customers. Existing customers may continue to use Cloud9. New projects should use an alternative such as AWS CloudShell (for shell tasks), Amazon CodeCatalyst Dev Environments (for full IDE), or a local IDE with AWS Toolkit.

### Environment Types

| Type | Description |
|---|---|
| **EC2 environment** | AWS provisions and manages an EC2 instance; Cloud9 connects via SSH over SSM (no open inbound port required since 2021); supports instance type selection; instance can be stopped/started to save costs |
| **SSH environment** | Cloud9 connects to any SSH-accessible server you control (on-premises, EC2 without SSM, third-party VMs); you manage the server; requires Node.js and a specific Cloud9 installer on the server |

### EC2 Instance Options

- Instance types: t2.micro through larger compute families
- Storage: EBS volume attached to the EC2 instance (default 10 GB)
- Networking: Launched in a VPC subnet; can access private resources within the VPC
- Connection type: SSM (recommended; no inbound security group rules needed) or SSH (requires port 22 open)

### Environment Sharing

| Role | Permissions |
|---|---|
| **Owner** | Full control; can share/delete the environment; can see all open files and terminal |
| **Read/Write** | Can edit files, run terminals, execute code |
| **Read-only** | Can view files and terminal output but cannot make changes |

Sharing is done by adding AWS IAM users or IAM Identity Center users as members. Collaboration is real-time (shared terminal, shared editor with cursors).

### Built-in IDE Features

| Feature | Description |
|---|---|
| **Integrated terminal** | Direct bash/zsh shell on the EC2 instance; multiple terminal tabs supported |
| **AWS CLI pre-configured** | IAM role credentials automatically available via instance metadata; no manual configuration needed |
| **Code editor** | Syntax highlighting, code folding, multi-cursor; file tree sidebar |
| **Code completion** | Language-aware completion for JavaScript, Python, PHP, Ruby, and more |
| **Debugger** | Built-in debugger for Node.js and Python; step through, set breakpoints, inspect variables |
| **Git integration** | Terminal-based Git; no graphical Git panel |
| **File tree** | Full file system navigation; create/rename/delete files and folders |
| **Split pane** | Multiple editor panes side by side |
| **Themes** | Light/dark themes; customizable color scheme |
| **Keybindings** | Default, Vim, Emacs, and Sublime Text keybinding modes |
| **Language runners** | Run Python, Node.js, Ruby, Go, PHP scripts directly via Run panel |
| **AWS Toolkit** | Pre-installed AWS Toolkit extension for Lambda invoke, Step Functions visualization, S3 browsing |

### Supported Languages (Syntax / Completion)

JavaScript / TypeScript, Python, PHP, Ruby, Go, Java, C/C++, HTML/CSS, Markdown, YAML, JSON, Bash, and more.

### Networking Considerations

- EC2 environment can be in a VPC to access private resources (RDS, ElastiCache, internal APIs)
- SSM-based connectivity does not require an internet gateway or inbound security group rule; ideal for private subnets
- "No-ingress" EC2 environments use SSM Session Manager for the IDE connection

---

## AWS CloudShell

**Purpose**: Browser-based, pre-authenticated shell environment available in the AWS Management Console. Provides instant access to AWS CLI v2 and common developer tools without provisioning or managing any infrastructure.

### Key Characteristics

| Attribute | Value |
|---|---|
| **Authentication** | Inherits IAM credentials of the signed-in console user; no configuration required |
| **Persistent storage** | 1 GB per AWS Region; persists across sessions; stored in `$HOME` (`/home/cloudshell-user`) |
| **Compute** | 1 vCPU, 2 GB RAM per session |
| **Session timeout** | Session terminates after 20 minutes of inactivity; environment and files are preserved |
| **OS** | Amazon Linux 2 (AL2) based |
| **Internet access** | Outbound internet access available by default; can be restricted via VPC mode |

### Pre-installed Tools

| Category | Tools |
|---|---|
| **AWS CLI** | AWS CLI v2 (latest) |
| **Runtime** | Python 3, Node.js, bash, zsh |
| **Utilities** | git, jq, make, zip/unzip, wget, curl, tar |
| **Container** | Docker (for building and running containers) |
| **IaC** | AWS SAM CLI, AWS CDK |
| **Text editors** | vim, nano |
| **Language tools** | pip, npm |

Custom tools can be installed into the persistent home directory (`$HOME`); installs in `/usr/local` do not persist across sessions.

### CloudShell Features

| Feature | Description |
|---|---|
| **Split pane** | Open multiple shell panes side by side in the same browser tab |
| **Multiple tabs** | Open multiple independent CloudShell sessions in separate browser tabs; each has its own shell process |
| **File transfer** | Upload files from your local machine to CloudShell; download files from CloudShell to local; accessible via the Actions menu |
| **Safe paste** | Prompts before pasting multi-line commands; reduces accidental execution |
| **Region selector** | Each CloudShell session is scoped to the AWS Region selected in the console; persistent storage is per-region |

### VPC Environment (Private CloudShell)

Launch CloudShell inside a VPC to access private resources (RDS, internal APIs, services without public endpoints):

| Attribute | VPC Mode Behavior |
|---|---|
| **VPC attachment** | Attaches an ENI to a specified VPC subnet |
| **Private access** | Can reach resources in the VPC (RDS, ElastiCache, private ALB) |
| **Internet access** | No direct internet access; must route through a NAT Gateway if needed |
| **Security groups** | Specify security groups controlling inbound/outbound traffic |

### CloudShell vs Cloud9 Quick Comparison

| | CloudShell | Cloud9 |
|---|---|---|
| Setup required | None (instant) | Create environment (1–2 min) |
| Persistent storage | 1 GB per region | Full EBS volume (10+ GB) |
| IDE features | Shell only | Full IDE (editor, debugger, file tree) |
| Collaboration | Single user | Shared environments |
| Cost | Free (included with AWS) | EC2 instance costs |
| Status | Active | Closed to new customers |
