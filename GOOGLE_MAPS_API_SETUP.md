# 🔑 Google Maps API Setup

## Getting API Key

1. **Go to Google Cloud Console:**
   https://console.cloud.google.com/

2. **Select project:** playground-332710

3. **Enable Google Maps API:**
   - Go to "APIs & Services" > "Library"
   - Find "Places API"
   - Click "Enable"

4. **Create API key:**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "API Key"
   - Copy the created key

5. **Restrict the key (recommended):**
   - Click on the created key
   - In "Application restrictions" select "HTTP referrers"
   - Add domains: `*.run.app`
   - In "API restrictions" select "Restrict key"
   - Select "Places API"

## Setting up the key in Cloud Run

```bash
gcloud run services update maps-to-waze-bot \
  --set-env-vars GOOGLE_MAPS_API_KEY=your_key_here \
  --region europe-central2
```

## Testing

After setting up the key, the bot will be able to process any Google Maps links, including:
- Place links without coordinates
- Short links maps.app.goo.gl
- Business and landmark links

## Cost

Google Maps API has a free tier:
- 1000 requests per day for Places API
- Additional requests: $0.017 per 1000 requests

This is sufficient for most bots. 