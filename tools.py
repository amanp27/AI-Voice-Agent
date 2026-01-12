import logging
from livekit.agents import function_tool
import requests
from langchain_community.tools import DuckDuckGoSearchRun
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Annotated

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@function_tool(description="Get the current weather for a given city")
async def get_weather(
    city: Annotated[str, "The city name to get weather for (e.g., 'London', 'New York', 'Tokyo')"]
) -> str:
    """
    Get the current weather for a given city.
    
    Args:
        city: Name of the city
    
    Returns:
        Current weather information for the specified city
    """
    try:
        response = requests.get(
            f"https://wttr.in/{city}?format=3",
            timeout=5
        )
        if response.status_code == 200:
            logger.info(f"Weather for {city}: {response.text.strip()}")
            return response.text.strip()   
        else:
            logger.error(f"Failed to get weather for {city}: {response.status_code}")
            return f"Could not retrieve weather for {city}. Please try again."
    except requests.exceptions.Timeout:
        logger.error(f"Timeout while getting weather for {city}")
        return f"Request timed out while getting weather for {city}."
    except Exception as e:
        logger.error(f"Error retrieving weather for {city}: {e}")
        return f"An error occurred while retrieving weather for {city}."


@function_tool(description="Search the web using DuckDuckGo to find current information")
async def search_web(
    query: Annotated[str, "The search query string"]
) -> str:
    """
    Search the web using DuckDuckGo to find current information.
    
    Args:
        query: The search query string
    
    Returns:
        Search results from DuckDuckGo
    """
    try:
        search_tool = DuckDuckGoSearchRun()
        results = search_tool.run(tool_input=query)
        logger.info(f"Search results for '{query}': {results[:100]}...")
        return results
    except Exception as e:
        logger.error(f"Error searching the web for '{query}': {e}")
        return f"An error occurred while searching the web. Please try again."
    

@function_tool(description="Send an email through Gmail")
async def send_email(
    to_email: Annotated[str, "Recipient email address"],
    subject: Annotated[str, "Email subject line"],
    message: Annotated[str, "Email body content"],
    cc_email: Annotated[str | None, "Optional CC email address"] = None
) -> str:
    """
    Send an email through Gmail.
    
    Args:
        to_email: Recipient email address
        subject: Email subject line
        message: Email body content
        cc_email: Optional CC email address
    
    Returns:
        Confirmation message or error description
    """
    try:
        # Gmail SMTP configuration
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        
        # Get credentials from environment variables
        gmail_user = os.getenv("GMAIL_USER")
        gmail_password = os.getenv("GMAIL_APP_PASSWORD")
        
        if not gmail_user or not gmail_password:
            logger.error("Gmail credentials not found in environment variables")
            return "Email sending failed: Gmail credentials not configured. Please contact the administrator."
        
        # Basic email validation
        if "@" not in to_email or "." not in to_email:
            return f"Invalid email address: {to_email}"
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = gmail_user
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add CC if provided
        recipients = [to_email]
        if cc_email:
            if "@" in cc_email and "." in cc_email:
                msg['Cc'] = cc_email
                recipients.append(cc_email)
            else:
                return f"Invalid CC email address: {cc_email}"
        
        # Attach message body
        msg.attach(MIMEText(message, 'plain'))
        
        # Connect to Gmail SMTP server
        with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
            server.starttls()
            server.login(gmail_user, gmail_password)
            server.sendmail(gmail_user, recipients, msg.as_string())
        
        logger.info(f"Email sent successfully to {to_email}")
        cc_info = f" (CC: {cc_email})" if cc_email else ""
        return f"Email sent successfully to {to_email}{cc_info}"
        
    except smtplib.SMTPAuthenticationError:
        logger.error("Gmail authentication failed")
        return "Email sending failed: Authentication error. Please check Gmail credentials."
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error occurred: {e}")
        return f"Email sending failed due to a server error. Please try again later."
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        return "An error occurred while sending the email. Please try again."