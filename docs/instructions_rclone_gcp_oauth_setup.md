# rclone OAuth Setup with Google Drive

This file summarizes the rationale, detailed setup steps, and key tips for rclone OAuth configuration with Google Drive.

## Overview

This setup uses **rclone with OAuth** (instead of a `service_account_file`) to access Google Drive. We chose this approach because:

- **Full Access:**  
  OAuth provides full access to "My Drive", whereas a service account only sees folders explicitly shared with it.
- **Better Suitability for Our Use Case:**  
  We need both mounting specific folders for read/write operations and comparing files across our entire drive.
- **Rate Limits & API Quotas:**  
  - **What’s Rate-Limited:** Google Drive API limits are based on the number of API calls rather than the data volume.  
    - **Example 1:** Transferring a single 10GB file uses relatively few API calls.  
    - **Example 2:** Frequently modifying and saving a small text file can trigger many API calls rapidly.
  - **Built-In OAuth vs. Custom OAuth:**  
    rclone’s built-in OAuth uses shared credentials and thus has stricter quotas. To avoid throttling during heavy use, we create our own OAuth client credentials from a dedicated GCP project.

## Step 1: Create OAuth Credentials in Your GCP Project

1. **Access Your GCP Project:**
   - Log in to the [Google Cloud Console](https://console.cloud.google.com/).
   - Select your project created for this purpose (e.g., name it `google-drive`).

2. **Enable the Google Drive API:**
   - Navigate to **APIs & Services > Library**.
   - Search for **Google Drive API** and click **Enable**.

3. **Configure the OAuth Consent Screen:**
   - Go to **APIs & Services > OAuth consent screen**.
   - **Audience:**  
     - Choose **External**.  
     - *Note:* Since you're using a personal (non-Google Workspace) account, you must use External. This places the app in testing mode, meaning it’s only available to users you add as test users (typically just you).
   - **App Information:**  
     - Enter an App Name.
     - Set the **User Support Email** (your email).
   - **Contact Information:**  
     - Provide your email address.
   - Accept the Google API Services: User Data Policy.
   - Click **Save and Continue**.

4. **Create an OAuth Client ID:**
   - Navigate to **APIs & Services > Credentials**.
   - Click **Create Credentials** and choose **OAuth client ID**.
   - Select **Desktop App** as the Application Type.
   - Name your client (e.g., "rclone OAuth Client").
   - Click **Create**.
   - **Store the Credentials:**  
     - Copy the **Client ID** and **Client Secret**.
     - Save a copy of the credentials JSON file to `~/.secrets/` for backup.

## Step 2: Configure rclone with Your New OAuth Credentials

1. **Start rclone Configuration:**
   ```bash
   rclone config
   ```

2. Create a New Remote:
   - Type n to create a new remote.
   - Name it `whatever_rclone_config`.

3. Select the Storage Type:
   - Choose Google Drive from the list.

4. Enter Your OAuth Credentials:
   - When prompted for client_id, enter the Client ID from your GCP project.
   - When prompted for client_secret, enter the Client Secret from your GCP project.

5. Set the Scope:
   - Choose the default drive scope for full read/write access.

6. Leave Unnecessary Fields Blank:
   - Root Folder ID: Leave blank (unless you want to restrict access to a specific folder).
   - Service Account File: Leave blank.

7. Advanced Configuration:
   - When asked "Edit advanced config? (y/n)", type n to skip advanced settings.

8. Auto Configuration:
   - When asked "Use auto config?", type y.
   - Your default browser will open. Log in with your Google account and grant the necessary permissions.
   - Once authentication is successful, rclone will save your access token.

9. Finish and Test:
   - Type q to exit the configuration.
   - Test the new remote by listing your drive contents:
     ```bash
     rclone lsd whatever_rclone_config:
     ```

## Notes & Tips
* Rate Limits:
  - API Call Limits: Google Drive API limits are based on the number of API calls per time period.
      + Large File Transfer: A single 10GB file transfer makes few API calls.
      + Frequent Small Updates: Repeatedly saving a small file can quickly accumulate many API calls.
  - Using Your Own OAuth Credentials:
    This provides higher quotas and more reliable performance compared to rclone's built-in (shared) OAuth credentials.

* Replicability:
  - Keep your OAuth credentials secure (stored in ~/.secrets/) and document your rclone configuration.
  - This documentation will help you quickly replicate the setup on a new machine or OS.

* Security:
  - Do not share your rclone.conf file publicly.
  - Keep your Client ID and Client Secret confidential.

* General rclone Tips:
  - Use rclone mount with the --vfs-cache-mode writes flag for reliable write operations.
  - Regularly test your setup with commands like rclone ls or rclone check to ensure everything is working as expected.
  - If you encounter rate limit issues, review your usage patterns and adjust accordingly.

