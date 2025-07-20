# Action Preview Feature Guide

This guide explains the new Action Preview functionality that shows a preview form before executing actions in the Global Search Page.

## 🎯 Overview

The Action Preview feature provides a better user experience by:
- Showing a preview form below the search bar when an action is clicked
- Allowing users to review and edit action details before execution
- Providing validation to ensure required fields are filled
- Offering a smooth flow from preview to execution

## 🔄 User Flow

1. **Click Action** → User clicks any quick action or trending task
2. **Show Preview** → Preview form appears below the search bar
3. **Review/Edit** → User can review and modify the action details
4. **Proceed/Cancel** → User can proceed to execute or cancel the action
5. **Execute** → Action executes with the updated details

## 📧 Email Actions Preview

When clicking email-related actions, the preview shows:

### Fields:
- **Recipients** - Email addresses (comma-separated)
- **Subject** - Email subject line
- **Message** - Email body content

### Smart Defaults:
- **Project Update Email** → Pre-filled with project update template
- **Follow-up Email** → Pre-filled with follow-up template
- **Thank You Email** → Pre-filled with appreciation template

### Validation:
- Recipients field must not be empty
- Subject field must not be empty
- Proceed button is disabled until validation passes

## 📅 Calendar/Meeting Actions Preview

When clicking calendar or meeting actions, the preview shows:

### Fields:
- **Event Title** - Meeting/event name
- **Date** - Event date (date picker)
- **Time** - Event start time (time picker)
- **Duration** - Meeting duration in minutes (15-480 min, 15 min steps)
- **Location** - Meeting location or "Google Meet"
- **Attendees** - Email addresses (comma-separated)
- **Description** - Event description
- **Include Google Meet** - Checkbox for video meetings

### Smart Defaults:
- **Team Standup** → 30 min duration, 9:00 AM time, standup description
- **Client Presentation** → 60 min duration, 2:00 PM time, presentation description
- **Team Meeting** → 60 min duration, 2:00 PM time, general meeting description

### Validation:
- Title field must not be empty
- Date field must not be empty
- Time field must not be empty
- Proceed button is disabled until validation passes

## 🎨 UI Features

### Visual Design:
- **Color-coded borders** based on action type (red for email, blue for calendar, green for meetings)
- **Icons** for each field type (users, clock, location, etc.)
- **Gradient proceed button** with hover effects
- **Validation states** with disabled/enabled button states

### Interactive Elements:
- **Edit/View toggle** - Switch between editing and viewing modes
- **Form validation** - Real-time validation with visual feedback
- **Smart placeholders** - Context-aware placeholder text
- **Responsive layout** - Works on desktop and mobile

## 🧪 Testing the Feature

### 1. Start the Application:
```bash
npm run dev
```

### 2. Navigate to Global Search Page:
- Open your browser to the app URL
- You should see the Global Search interface

### 3. Test Email Actions:
- Click "Send project update email" quick action
- Observe the email preview form below the search bar
- Try editing the recipients, subject, and body
- Click "Proceed to Execute" to continue

### 4. Test Calendar Actions:
- Click "Schedule team meeting" quick action
- Observe the calendar preview form
- Try changing the date, time, and duration
- Add attendees and modify the description
- Click "Proceed to Execute" to continue

### 5. Test Trending Tasks:
- Click any trending task (they have priority badges)
- Each task will show appropriate preview based on type
- Test the edit functionality and validation

### 6. Test Validation:
- Clear required fields (recipients for email, title for calendar)
- Notice the "Proceed" button becomes disabled
- Fill in required fields to re-enable the button

## 🔧 Console Logging

The feature includes console logging for debugging:
- `🎯 Action clicked:` - When an action is clicked
- `📋 Generated preview data:` - Preview data structure
- `✅ Proceeding with action:` - When user proceeds
- `❌ Action preview cancelled:` - When user cancels

## 🎯 Action Types Supported

### Email Actions:
- Send project update email
- Compose follow-up email
- Send thank you email
- Any action containing "email", "send", or "compose"

### Calendar Actions:
- Schedule team meeting
- Schedule weekly standup
- Any action containing "calendar", "schedule", or "meeting"

### Meeting Actions:
- Create Google Meet for standup
- Create Google Meet for presentation
- Any action containing "meet" or "video"

### Other Actions:
- Daily briefing
- Generic actions (show simple confirmation)

## 🚀 Future Enhancements

Planned improvements:
- **Attachment support** for emails
- **Recurring events** for calendar
- **Template library** for common actions
- **Contact suggestions** for recipients/attendees
- **Time zone support** for meetings
- **Rich text editor** for email body
- **Calendar integration** for availability checking

## 🐛 Troubleshooting

### Preview Not Showing:
- Check browser console for errors
- Ensure action contains recognized keywords
- Verify component imports are correct

### Validation Issues:
- Check required fields are filled
- Ensure email format is valid
- Verify date/time formats are correct

### Styling Issues:
- Check Tailwind CSS classes are loading
- Verify component UI library imports
- Ensure theme context is working

The Action Preview feature provides a much better user experience by allowing users to review and customize their actions before execution, reducing errors and improving confidence in the system.
