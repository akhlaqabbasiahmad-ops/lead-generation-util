# Email Marketing Feature Guide

## Overview

The application now includes comprehensive email marketing functionality to send emails to your scraped leads.

## Features

✅ **SMTP Configuration** - Support for Gmail, Outlook, and other SMTP servers
✅ **Email Templates** - Pre-built templates (Introduction, Follow-up, Partnership)
✅ **Personalization** - Use {name}, {company}, {email}, {phone}, {address}, {website}
✅ **Bulk Email Sending** - Send to multiple leads from scraped files
✅ **Test Email** - Send test emails before campaigns
✅ **Connection Testing** - Test SMTP connection before sending
✅ **Progress Tracking** - Real-time email sending status

## How to Use

### Step 1: Access Email Marketing Tab

1. Open the web interface: `http://16.16.249.160`
2. Click on the **"📧 Email Marketing"** tab

### Step 2: Configure SMTP Settings

**For Gmail:**
- SMTP Server: `smtp.gmail.com`
- SMTP Port: `587` (TLS) or `465` (SSL)
- Username: Your Gmail address
- Password: **App Password** (not your regular password)
  - Generate at: https://myaccount.google.com/apppasswords

**For Outlook/Office 365:**
- SMTP Server: `smtp.office365.com`
- SMTP Port: `587`
- Username: Your Outlook email
- Password: Your email password

**For Other Providers:**
- Check your email provider's SMTP settings
- Common ports: 587 (TLS), 465 (SSL), 25 (Plain)

### Step 3: Test Connection

1. Fill in SMTP settings
2. Click **"Test Connection"** button
3. Wait for confirmation

### Step 4: Create Email Content

**Option A: Use Pre-built Templates**
- Select template from dropdown:
  - **Introduction Email** - First contact template
  - **Follow-up Email** - Follow-up template
  - **Partnership Opportunity** - Partnership template

**Option B: Custom Template**
- Select "Custom Template"
- Write your own subject and body
- Use personalization fields: {name}, {company}, {email}, etc.

### Step 5: Select Leads

**Option A: From Scraped File**
- Select "From Scraped File"
- Choose a file from the dropdown (Excel/CSV files)

**Option B: Current Results**
- Select "Use Current Results"
- Uses leads from your last scrape

### Step 6: Send Test Email (Optional)

1. Enter your email address
2. Click **"Send Test Email"**
3. Verify the email looks correct

### Step 7: Send Campaign

1. Click **"Send Email Campaign"**
2. Monitor progress in status bar
3. Wait for completion notification

## Personalization Fields

Use these in your email subject and body:

- `{name}` - Business owner/contact name
- `{company}` - Company/business name
- `{email}` - Email address
- `{phone}` - Phone number
- `{address}` - Business address
- `{website}` - Website URL
- `{sender_name}` - Your name (from "From Name" field)

**Example:**
```
Subject: Hello {name} - Partnership Opportunity for {company}

Body: 
Dear {name},

I came across {company} and was impressed by your business at {address}.
Would you like to discuss partnership opportunities?

Best regards,
{sender_name}
```

## API Endpoints

### Test SMTP Connection
```
POST /api/email/test-connection
Body: {
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_username": "your-email@gmail.com",
  "smtp_password": "your-password",
  "from_email": "your-email@gmail.com",
  "from_name": "Your Name"
}
```

### Get Email Templates
```
GET /api/email/templates
Returns: Available email templates
```

### Send Test Email
```
POST /api/email/send-test
Body: {
  "smtp_server": "...",
  "smtp_port": 587,
  "smtp_username": "...",
  "smtp_password": "...",
  "from_email": "...",
  "from_name": "...",
  "subject": "Test Email",
  "body_html": "<p>Test</p>",
  "test_email": "test@example.com"
}
```

### Send Email Campaign
```
POST /api/email/send
Body: {
  "smtp_server": "...",
  "smtp_port": 587,
  "smtp_username": "...",
  "smtp_password": "...",
  "from_email": "...",
  "from_name": "...",
  "template": "intro",
  "subject": "Hello {name}",
  "body_html": "<p>Hello {name}...</p>",
  "leads_source": "file",
  "leads_file": "leads.xlsx"
}
```

### Get Email Status
```
GET /api/email/status
Returns: Current email sending status and results
```

## Gmail App Password Setup

1. Go to: https://myaccount.google.com/apppasswords
2. Sign in to your Google account
3. Select "Mail" and "Other (Custom name)"
4. Enter "Google Scraper" as the name
5. Click "Generate"
6. Copy the 16-character password
7. Use this password (not your regular Gmail password) in SMTP settings

## Best Practices

1. **Always Test First** - Send a test email before campaigns
2. **Use Personalization** - Makes emails more effective
3. **Respect Rate Limits** - System delays between emails automatically
4. **Check Spam Folders** - Some emails may go to spam
5. **Follow Email Laws** - Include unsubscribe options for compliance
6. **Monitor Results** - Check success/failure rates

## Troubleshooting

### "Connection Failed"
- Check SMTP server and port
- Verify username and password
- For Gmail, use App Password (not regular password)
- Check firewall/network restrictions

### "Email Not Received"
- Check spam/junk folder
- Verify recipient email is correct
- Check SMTP logs for errors
- Some providers block bulk emails

### "Rate Limiting"
- System automatically delays between emails
- Reduce batch size if needed
- Wait between campaigns

## Security Notes

⚠️ **Important:**
- Never share your SMTP credentials
- Use App Passwords for Gmail (not regular passwords)
- Store credentials securely
- Consider using environment variables for production

## Files Created

- `email_marketing.py` - Email marketing module
- `EMAIL_MARKETING_GUIDE.md` - This guide
- Updated `app.py` - Added email endpoints
- Updated `templates/index.html` - Added email marketing UI

## Next Steps

1. Access the Email Marketing tab in the web interface
2. Configure your SMTP settings
3. Test the connection
4. Create your first email campaign!

