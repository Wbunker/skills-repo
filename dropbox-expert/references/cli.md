# Dropbox CLI Tools

Two options for shell/CLI access:

1. **dbxcli** — Go-based, Dropbox-maintained (but unsupported)
2. **Dropbox-Uploader** — Pure bash, community-maintained

---

## dbxcli

**Repo**: `github.com/dropbox/dbxcli`
**Note**: Officially "no formal Dropbox support" — bugs may or may not get fixed. Requires your own API credentials baked in.

### Installation

**macOS (Homebrew)**:
```bash
brew install dbxcli
```

**Pre-compiled binary**:
```bash
# macOS
curl -L https://github.com/dropbox/dbxcli/releases/latest/download/dbxcli-darwin-amd64 -o dbxcli
chmod +x dbxcli && sudo mv dbxcli /usr/local/bin/

# Linux
curl -L https://github.com/dropbox/dbxcli/releases/latest/download/dbxcli-linux-amd64 -o dbxcli
chmod +x dbxcli && sudo mv dbxcli /usr/local/bin/
```

**From source** (with your own API credentials):
```bash
# Edit root.go to set personalAppKey and personalAppSecret before building
git clone https://github.com/dropbox/dbxcli
cd dbxcli
# Edit root.go: set personalAppKey = "YOUR_APP_KEY"
#                    personalAppSecret = "YOUR_APP_SECRET"
go build -o dbxcli .
```

### Authentication

```bash
dbxcli account   # Opens browser for OAuth, saves token locally
```

### File Commands

```bash
# List files/folders
dbxcli ls                        # List root
dbxcli ls /folder                # List specific folder
dbxcli ls -l /folder             # Long format with sizes

# Download
dbxcli get /remote/file.txt local/file.txt

# Upload
dbxcli put local/file.txt /remote/file.txt

# Copy
dbxcli cp /source/file.txt /dest/file.txt

# Move / Rename
dbxcli mv /old/path.txt /new/path.txt

# Create directory
dbxcli mkdir /new/folder

# Delete
dbxcli rm /remote/file.txt

# Disk usage
dbxcli du                        # Total usage
dbxcli du /folder                # Usage of specific folder

# Search
dbxcli search "query term"

# File revisions
dbxcli revs /remote/file.txt

# Restore a revision
dbxcli restore /remote/file.txt REV_HASH
```

### Team Commands (Business accounts)

```bash
dbxcli team info                          # Team info
dbxcli team list-members                  # List all team members
dbxcli team list-groups                   # List groups
dbxcli team add-member email display_name # Add a member
dbxcli team remove-member email           # Remove a member
```

### Scripting examples

```bash
#!/bin/bash
# Upload all PDFs from a local folder
for f in /local/reports/*.pdf; do
    dbxcli put "$f" "/Dropbox/Reports/$(basename $f)"
done

# Download all files from a Dropbox folder
dbxcli ls /backup | awk '{print $NF}' | while read path; do
    dbxcli get "$path" "./local/$(basename $path)"
done

# Check if file exists
if dbxcli ls /folder/file.txt &>/dev/null; then
    echo "exists"
fi
```

---

## Dropbox-Uploader

**Repo**: `github.com/andreafabrizi/Dropbox-Uploader`
Pure bash script — only requires `curl`. No compilation needed.
**Important**: If you configured this before September 30, 2021, you must reconfigure — the old OAuth1 tokens no longer work.

### Setup

```bash
# Download the script
curl -O https://raw.githubusercontent.com/andreafabrizi/Dropbox-Uploader/master/dropbox_uploader.sh
chmod +x dropbox_uploader.sh

# First run — walks through OAuth2/PKCE setup interactively
./dropbox_uploader.sh
# Follow prompts: creates a Dropbox app, pastes auth code
# Token saved to ~/.dropbox_uploader
```

### Commands

```bash
SCRIPT="./dropbox_uploader.sh"

# Upload
$SCRIPT upload local_file.txt /remote/file.txt
$SCRIPT upload /local/folder/ /remote/folder/   # Recursive folder upload (-r flag may be needed)

# Download
$SCRIPT download /remote/file.txt local_file.txt
$SCRIPT download /remote/folder/ /local/folder/

# List
$SCRIPT list /remote/folder

# Info / quota
$SCRIPT info

# Create directory
$SCRIPT mkdir /new/folder

# Delete
$SCRIPT delete /remote/file.txt

# Move
$SCRIPT move /old/path.txt /new/path.txt

# Copy
$SCRIPT copy /source/file.txt /dest/file.txt

# Share (creates a shared link and prints it)
$SCRIPT share /remote/file.txt

# Check if file exists (returns 0 if exists)
$SCRIPT exists /remote/file.txt
```

### Scripting with Dropbox-Uploader

```bash
#!/bin/bash
DROPBOX="./dropbox_uploader.sh"

# Backup with timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
$DROPBOX upload /local/backup.tar.gz "/backups/backup_${TIMESTAMP}.tar.gz"

# Upload only new files
for f in /local/docs/*.pdf; do
    remote="/Docs/$(basename "$f")"
    if ! $DROPBOX exists "$remote"; then
        $DROPBOX upload "$f" "$remote"
        echo "Uploaded: $f"
    fi
done

# Sync a folder (upload all files)
find /local/sync_folder -type f | while read file; do
    relative="${file#/local/sync_folder/}"
    $DROPBOX upload "$file" "/sync_folder/${relative}"
done
```

### Environment variables

```bash
# Use a different config file (for multiple accounts)
CONFIGFILE=~/.dropbox_account2 ./dropbox_uploader.sh list /
```

---

## Comparison

| Feature | dbxcli | Dropbox-Uploader |
|---------|--------|-----------------|
| Dependencies | Go binary (self-contained) | bash + curl |
| Auth setup | Simpler OAuth | Interactive PKCE setup |
| File ops | Full suite | Full suite |
| Team support | Yes | No |
| Revisions | Yes | No |
| Search | Yes | No |
| Maintenance | Low (Dropbox, unsupported) | Active (community) |
| Credentials | Compiled in or App Console | ~/.dropbox_uploader config |
