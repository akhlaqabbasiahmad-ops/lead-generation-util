# AWS SES (Simple Email Service) Setup Guide

## Why Use AWS SES?

If you're having connection issues with Gmail/Outlook on EC2, AWS SES is a better solution:
- ✅ Works natively on EC2 (no firewall issues)
- ✅ Better deliverability
- ✅ Higher sending limits
- ✅ No SMTP port blocking issues
- ✅ Integrated with AWS

## Step 1: Set Up AWS SES

### 1.1 Go to AWS SES Console

1. Open AWS Console
2. Search for "SES" or "Simple Email Service"
3. Click on "Simple Email Service"

### 1.2 Verify Your Email Address (Sandbox Mode)

**If you're in SES Sandbox (default):**
1. Click "Verified identities" → "Create identity"
2. Select "Email address"
3. Enter your email address
4. Click "Create identity"
5. Check your email and click verification link

**To send to any email (move out of Sandbox):**
1. Click "Account dashboard"
2. Click "Request production access"
3. Fill out the form (explain your use case)
4. Wait for approval (usually 24-48 hours)

### 1.3 Get SMTP Credentials

1. Click "SMTP settings" (left sidebar)
2. Click "Create SMTP credentials"
3. Enter an IAM user name (e.g., "email-sender")
4. Click "Create"
5. **IMPORTANT:** Download the credentials CSV file
   - Contains: SMTP Username and SMTP Password
   - Save this securely!

### 1.4 Get Your SES SMTP Endpoint

Your SES SMTP endpoint depends on your AWS region:

| Region | SMTP Server | Port |
|--------|------------|------|
| US East (N. Virginia) | email-smtp.us-east-1.amazonaws.com | 587 |
| US West (Oregon) | email-smtp.us-west-2.amazonaws.com | 587 |
| EU (Ireland) | email-smtp.eu-west-1.amazonaws.com | 587 |
| Asia Pacific (Singapore) | email-smtp.ap-southeast-1.amazonaws.com | 587 |

**Find your region's endpoint:**
1. In SES Console, look at the URL: `https://console.aws.amazon.com/ses/home?region=us-east-1`
2. The region code is in the URL
3. Use the corresponding SMTP server from the table above

## Step 2: Configure in Application

### 2.1 Use SES SMTP Settings

In the Email Marketing tab:

**SMTP Preset:** Select "Custom SMTP"

**SMTP Server:** 
- Use your region's SES endpoint (e.g., `email-smtp.us-east-1.amazonaws.com`)

**SMTP Port:** 
- `587` (TLS - Recommended)

**SMTP Username:** 
- From the credentials CSV file you downloaded

**SMTP Password:** 
- From the credentials CSV file you downloaded

**From Email:** 
- Your verified email address in SES

**From Name:** 
- Your company/name

### 2.2 Test Connection

1. Click "Test Connection"
2. Should work immediately (no firewall issues!)

## Step 3: Send Emails

1. Configure email content
2. Select recipients
3. Click "Send Email Campaign"
4. Emails will be sent via AWS SES

## Benefits of AWS SES

✅ **No Firewall Issues** - Works natively on EC2
✅ **Better Deliverability** - AWS infrastructure
✅ **Higher Limits** - 200 emails/day (sandbox), 50,000+ (production)
✅ **Cost Effective** - $0.10 per 1,000 emails
✅ **No Port Blocking** - Uses standard AWS endpoints

## Troubleshooting

### "Email address not verified"

- You're in Sandbox mode
- Verify your email address in SES Console
- Or request production access

### "Account is in sandbox mode"

- Can only send to verified email addresses
- Request production access to send to any email

### "Access Denied"

- Check SMTP credentials are correct
- Make sure you downloaded the CSV file
- Credentials are different from AWS console login

## Cost

- **Free Tier:** 62,000 emails/month (if sent from EC2)
- **After Free Tier:** $0.10 per 1,000 emails
- Very cost-effective for email marketing!

## Next Steps

1. Set up SES in AWS Console
2. Verify your email address
3. Get SMTP credentials
4. Configure in the application
5. Start sending emails!

