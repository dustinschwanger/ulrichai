# Debugging Sources Display Issue

## Current Status
✅ Backend API is correctly returning sources (verified via test)
✅ Added extensive debug logging to track data flow
✅ Restarted development server with debugging code

## Test Instructions

1. **Open the app** at http://localhost:3000

2. **Open Browser Developer Console** (F12 or Cmd+Option+I)

3. **Ask a test question** like:
   - "What are the key dimensions of effective leadership?"
   - "How can HR create more value for the business?"

4. **Watch the Console** for these debug messages:

   ### Expected Console Output:
   ```
   Making API request to: https://ulrichai-production.up.railway.app/api/chat/query
   API Response: {answer: "...", sources: [...]}
   Sources from API: [Array of sources]
   Number of sources: 4

   MessageBubble - Sources received: [Array]
   MessageBubble - Number of sources: 4

   MessageBubble - Checking source display conditions:
     - isUser: false
     - message.sources: [Array]
     - message.sources.length: 4
     - Will show sources: true

   SourceCards component - sources prop: [Array]
   SourceCards - sources length: 4
   ```

## What to Check

1. **If you see "Sources from API: undefined"**
   - The API isn't returning sources field

2. **If you see "SourceCards - returning null because no sources"**
   - Sources aren't being passed to the component

3. **If you see "Will show sources: false"**
   - One of the conditions is failing in MessageBubble

## Manual Test
Open `test_sources.html` in your browser and click "Test API with Sources" to verify the API directly.

## API Verification
The Railway API at https://ulrichai-production.up.railway.app IS returning sources correctly.

## Key Files Modified
- `/src/components/Chat/index.tsx` - Added API response logging
- `/src/components/Chat/MessageBubble.tsx` - Added source display condition logging
- `/src/components/Chat/SourceCards.tsx` - Added component input logging

## Next Steps Based on Console Output
Report back what you see in the console, and we can identify exactly where the sources are getting lost in the data flow.