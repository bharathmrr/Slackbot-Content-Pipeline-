"""
Message formatting utilities for Slack responses.
"""

from typing import Dict, List, Any
from datetime import datetime


class MessageFormatter:
    """Formats messages for Slack with consistent styling."""
    
    def format_upload_instructions(self) -> Dict[str, Any]:
        """Format upload instructions message."""
        return {
            "text": "📁 Upload Keywords",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "📁 Upload Your Keywords"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Please upload a CSV file containing your keywords. The file should have:\n\n• One keyword per row\n• A header column named 'keyword', 'keywords', 'term', or 'query'\n• Maximum 1000 keywords per file"
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": "💡 *Tip:* You can also use `/keywords paste` to paste keywords directly"
                        }
                    ]
                }
            ]
        }
    
    def format_paste_instructions(self) -> Dict[str, Any]:
        """Format paste instructions message."""
        return {
            "text": "📝 Paste Keywords",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "📝 Paste Your Keywords"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Please paste your keywords in your next message. You can format them as:\n\n• Comma-separated: `keyword1, keyword2, keyword3`\n• Line-separated (one per line)\n• Mixed format\n\nI'll automatically detect and process them!"
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": "📊 Maximum 1000 keywords per batch"
                        }
                    ]
                }
            ]
        }
    
    def format_keywords_uploaded(self, batch_id: str, keyword_count: int) -> Dict[str, Any]:
        """Format keywords uploaded confirmation."""
        return {
            "text": f"✅ Keywords uploaded successfully! Batch ID: {batch_id}",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"✅ *Keywords uploaded successfully!*\n\n📊 *Batch ID:* `{batch_id}`\n📝 *Keywords:* {keyword_count}\n🚀 *Next step:* Use `/process {batch_id}` to start processing"
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "🚀 Start Processing"
                            },
                            "value": f"process_{batch_id}",
                            "action_id": "start_processing"
                        }
                    ]
                }
            ]
        }
    
    def format_processing_started(self, batch_id: str, keyword_count: int) -> Dict[str, Any]:
        """Format processing started message."""
        return {
            "text": f"🚀 Processing started for batch {batch_id}",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🚀 Processing Started"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Batch ID:* `{batch_id}`\n*Keywords:* {keyword_count}\n*Status:* Processing...\n\n⏳ This may take a few minutes. I'll update you on progress!"
                    }
                }
            ]
        }
    
    def format_processing_step(self, step_name: str, current: int, total: int) -> Dict[str, Any]:
        """Format processing step update."""
        progress_bar = "█" * current + "░" * (total - current)
        percentage = int((current / total) * 100)
        
        return {
            "text": f"🔄 Step {current}/{total}: {step_name}",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"🔄 *Step {current}/{total}: {step_name}*\n\n`{progress_bar}` {percentage}%"
                    }
                }
            ]
        }
    
    def format_processing_completed(self, batch_id: str, groups_count: int, ideas_count: int, download_url: str) -> Dict[str, Any]:
        """Format processing completed message."""
        return {
            "text": f"✅ Processing completed for batch {batch_id}",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "✅ Processing Completed!"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Batch ID:* `{batch_id}`\n*Results:*\n• 📊 Keyword groups: {groups_count}\n• 💡 Post ideas: {ideas_count}\n• 📄 Report: Ready for download"
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "📄 Download Report"
                            },
                            "url": download_url,
                            "action_id": "download_report"
                        }
                    ]
                }
            ]
        }
    
    def format_history(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Format user history."""
        history_text = ""
        for batch in history:
            date = datetime.fromisoformat(batch["created_at"]).strftime("%Y-%m-%d %H:%M")
            status_emoji = "✅" if batch["status"] == "completed" else "⏳" if batch["status"] == "processing" else "❌"
            history_text += f"• {status_emoji} `{batch['id']}` - {date} - {batch['keyword_count']} keywords\n"
        
        return {
            "text": "📋 Your Processing History",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "📋 Your Processing History"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": history_text or "No processing history found."
                    }
                }
            ]
        }
    
    def format_help_message(self) -> Dict[str, Any]:
        """Format help message."""
        return {
            "text": "🤖 Content Pipeline Bot Help",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🤖 Content Pipeline Bot"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Available Commands:*\n\n• `/keywords upload` - Upload CSV file with keywords\n• `/keywords paste` - Paste keywords directly\n• `/process <batch_id>` - Start processing keywords\n• `/history` - View your processing history\n• `/regenerate <batch_id>` - Regenerate outlines"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*What I do:*\n• 🔍 Group keywords semantically\n• 📝 Generate content outlines\n• 💡 Suggest post ideas\n• 📄 Create comprehensive reports\n• 📧 Email reports (optional)"
                    }
                }
            ]
        }
    
    def format_no_keywords_found(self) -> Dict[str, Any]:
        """Format no keywords found message."""
        return {
            "text": "❌ No keywords found",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "❌ *No valid keywords found*\n\nPlease check your input format. Keywords should be:\n• Comma-separated or line-separated\n• At least 2 characters long\n• Contain at least one letter"
                    }
                }
            ]
        }
    
    def format_batch_not_found(self) -> Dict[str, Any]:
        """Format batch not found message."""
        return {
            "text": "❌ Batch not found",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "❌ *Batch not found*\n\nPlease check the batch ID and try again. Use `/history` to see your recent batches."
                    }
                }
            ]
        }
    
    def format_unauthorized_batch(self) -> Dict[str, Any]:
        """Format unauthorized batch access message."""
        return {
            "text": "🔒 Access denied",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "🔒 *Access denied*\n\nYou can only process your own keyword batches."
                    }
                }
            ]
        }
    
    def format_already_processing(self) -> Dict[str, Any]:
        """Format already processing message."""
        return {
            "text": "⚠️ Already processing",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "⚠️ *This batch is already being processed*\n\nPlease wait for the current processing to complete."
                    }
                }
            ]
        }
    
    def format_processing_failed(self, batch_id: str) -> Dict[str, Any]:
        """Format processing failed message."""
        return {
            "text": f"❌ Processing failed for batch {batch_id}",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"❌ *Processing failed for batch `{batch_id}`*\n\nPlease try again later or contact support if the issue persists."
                    }
                }
            ]
        }
    
    def format_rate_limit_exceeded(self) -> Dict[str, Any]:
        """Format rate limit exceeded message."""
        return {
            "text": "⚠️ Rate limit exceeded",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "⚠️ *Rate limit exceeded*\n\nYou've made too many requests. Please wait a few minutes before trying again."
                    }
                }
            ]
        }
    
    def format_error_message(self) -> Dict[str, Any]:
        """Format generic error message."""
        return {
            "text": "❌ An error occurred",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "❌ *An error occurred*\n\nPlease try again later. If the problem persists, contact support."
                    }
                }
            ]
        }
    
    def format_keyword_detection(self, text_preview: str) -> Dict[str, Any]:
        """Format keyword detection message."""
        return {
            "text": "🔍 Keywords detected",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"🔍 *I detected potential keywords in your message:*\n\n`{text_preview}...`\n\nWould you like me to process these as keywords?"
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "✅ Yes, process them"
                            },
                            "value": "process_detected_keywords",
                            "action_id": "process_keywords"
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "❌ No, ignore"
                            },
                            "value": "ignore_keywords",
                            "action_id": "ignore_keywords"
                        }
                    ]
                }
            ]
        }
    
    def format_email_sent(self) -> Dict[str, Any]:
        """Format email sent confirmation."""
        return {
            "text": "📧 Report emailed",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "📧 *Report has been emailed to you!*\n\nCheck your inbox for the detailed PDF report."
                    }
                }
            ]
        }
    
    def format_process_usage(self) -> Dict[str, Any]:
        """Format process command usage."""
        return {
            "text": "Usage: /process <batch_id>",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Usage:* `/process <batch_id>`\n\nExample: `/process batch_123`\n\nUse `/history` to see your available batches."
                    }
                }
            ]
        }
    
    def format_regenerate_usage(self) -> Dict[str, Any]:
        """Format regenerate command usage."""
        return {
            "text": "Usage: /regenerate <batch_id>",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Usage:* `/regenerate <batch_id>`\n\nThis will regenerate outlines for the specified batch with fresh web research."
                    }
                }
            ]
        }
    
    def format_no_history(self) -> Dict[str, Any]:
        """Format no history message."""
        return {
            "text": "📋 No processing history",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "📋 *No processing history found*\n\nStart by uploading keywords with `/keywords upload` or `/keywords paste`."
                    }
                }
            ]
        }
    
    def format_no_groups_found(self) -> Dict[str, Any]:
        """Format no groups found message."""
        return {
            "text": "❌ No groups found",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "❌ *No keyword groups found for this batch*\n\nThe batch may not have been processed yet. Use `/process <batch_id>` first."
                    }
                }
            ]
        }
    
    def format_regeneration_started(self, batch_id: str) -> Dict[str, Any]:
        """Format regeneration started message."""
        return {
            "text": f"🔄 Regenerating outlines for batch {batch_id}",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"🔄 *Regenerating outlines for batch `{batch_id}`*\n\nThis will update all outlines with fresh web research. Please wait..."
                    }
                }
            ]
        }
    
    def format_regeneration_completed(self, batch_id: str) -> Dict[str, Any]:
        """Format regeneration completed message."""
        return {
            "text": f"✅ Outlines regenerated for batch {batch_id}",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"✅ *Outlines regenerated successfully for batch `{batch_id}`*\n\nAll outlines have been updated with fresh competitive research."
                    }
                }
            ]
        }
