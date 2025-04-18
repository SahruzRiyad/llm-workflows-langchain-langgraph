# Add your utilities or helper functions to this file.

import os
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI
import base64
from io import BytesIO
from PIL import Image
from IPython.display import display, HTML, Markdown


# Params
async def visualizeCourses(result, screenshot, target_url, instructions, base_url):
    # Run the async process that returns an instance of DeeplearningCourseList and screenshot bytes
    

    if result:
        # Convert each course to a dict (using model_dump from Pydantic v2)
        courses_data = [course.model_dump() for course in result.courses]

        for course in courses_data:
          if course['courseURL']:
            course['courseURL'] = f'<a href="{base_url}{course["courseURL"]}" target="_blank">{course["title"]}</a>'


        # Build an HTML table if course data is available
        if courses_data:
            # Extract headers from the first course
            headers = courses_data[0].keys()
            table_html = '<table style="border-collapse: collapse; width: 100%;">'
            table_html += '<thead><tr>'
            for header in headers:
                table_html += (
                    f'<th style="border: 1px solid #dddddd; text-align: left; padding: 8px;">'
                    f'{header}</th>'
                )
            table_html += '</tr></thead>'
            table_html += '<tbody>'
            for course in courses_data:
                table_html += '<tr>'
                for header in headers:
                    value = course[header]
                    # If the field is "imageUrl", embed the image in the table cell
                    if header == "imageUrl":
                        value = (f'<img src="{value}" alt="Course Image" '
                                 f'style="max-width:100px; height:auto;">')
                    elif isinstance(value, list):
                        value = ', '.join(value)
                    table_html += (
                        f'<td style="border: 1px solid #dddddd; text-align: left; padding: 8px;">'
                        f'{value}</td>'
                    )
                table_html += '</tr>'
            table_html += '</tbody></table>'
        else:
            table_html = "<p>No course data available.</p>"

        # Display the course data table
        display(Markdown("### Scraped Course Data:"))
        display(HTML(table_html))

        # Convert the screenshot bytes into a base64 string and embed it in an <img> tag
        img_b64 = base64.b64encode(screenshot).decode('utf-8')
        img_html = (
            f'<img src="data:image/png;base64,{img_b64}" '
            f'alt="Website Screenshot" style="max-width:100%; height:auto;">'
        )
        display(Markdown("### Website Screenshot:"))
        display(HTML(img_html))
