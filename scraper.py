import requests
from bs4 import BeautifulSoup
import pandas as pd
universities_list_url = 'https://www.idp.com/india/blog/top-universities-abroad-indian-students-rankings-costs/'
universities_list_html = requests.get(universities_list_url).text
soup = BeautifulSoup(universities_list_html,'lxml')
uni_links = soup.find_all('a',class_='externalUrls')[:10]
university_links = []
# Getting links of universities
for element in uni_links:
    link = element.get('href')
    university_links.append(link)

university_data = []
course_data = []

print('*'*50)
print('Scraping Process started')
print('*'*50)

for i,uni_url in enumerate(university_links,start=1):
    print(f"Scraping university {i}/{len(university_links)}...")
    response = requests.get(uni_url).text
    soup = BeautifulSoup(response,'lxml')
    # University Id
    uni_id = f'U{i}'
    # University Name
    uni_name = soup.find('h1',class_='text-white c-lg:text-grey text-heading-3 c-xl:text-heading-1 text-truncate').text
    # University Country
    uni_country = soup.find('p',class_='text-heading-6').text
    # Getting University website and applying validation
    accordion_div = soup.find('div', class_='accordion')
    if accordion_div:
        link_tag = accordion_div.find('a')
        if link_tag and link_tag.has_attr('href'):
            uni_website = link_tag['href']
        else:
            uni_website = 'Not available'
    else:
        uni_website = 'Not available' 
    # Getting link for courses provided by University
    course_link = 'https://www.idp.com/'+soup.find('a',class_='btn btn--lg btn--grey-outline hidden c-lg:inline-block').get('href')
    response1 = requests.get(course_link).text
    soup1 = BeautifulSoup(response1,'lxml')
    # List of Courses
    courses = soup1.find_all('div',class_='c-lg:min-h-[425px] interactive-card border border-grey-medium h-full bg-white px-[20px] c-lg:px-[24px] py-[20px] flex flex-col gap-x-[8px] rounded-[12px] group hover:border-primary-petal transition-all')[:10]
    for j,course in enumerate(courses,start=1):
        # Course Id
        course_id = f'{uni_id}_C{j}'
        # Course Name
        course_name = course.find('a').text
        
        spans = course.find_all('span')
        # Default values
        course_level = next_intake = course_eligibility = course_fee = uni_city = 'Not Available'
        # Iterating through span tags containing the values
        for span in spans:
            text = span.text.strip()

            if "Bachelor" in text or "Master" in text or "Ph.D" in text:
                course_level = text

            elif "intake" in text:
                next_intake = text.split(':')[-1].strip()

            elif "IELTS" in text:
                course_eligibility = text.split(':')[-1].strip()

            elif "USD" in text or "GBP" in text:
                course_fee = text

            elif "," in text:  
                uni_city = text.split(',')[0].strip()
        # Appending the Course data
        course_data.append({
            "Course_id":course_id,
            "University_id":uni_id,
            "Course_Name":course_name,
            "Course_Level":course_level,
            "Next_Intake":next_intake,
            "Course_Eligibility":course_eligibility,
            "Course_Fee":course_fee,
        })
    # Appending the University data
    university_data.append({
        "University_id":uni_id,
        "University_Name":uni_name,
        "University_Country":uni_country,
        "University_City":uni_city,
        "University_Website":uni_website,
    })
print("\nScraping finished successfully!")

# Creating dataframes using pandas
university_df = pd.DataFrame(university_data)
course_df = pd.DataFrame(course_data)

# Writing the dataframes to Excelfile
with pd.ExcelWriter('Universities_Data.xlsx') as writer:
    university_df.to_excel(writer,sheet_name='Universities',index=False)
    course_df.to_excel(writer,sheet_name="Courses",index=False)
    # Adjusting the width of columns according to the max length of data in the column
    for sheet in writer.sheets.values():
        for column in sheet.columns:
            length = max(len(str(cell.value)) if cell.value else 0 for cell in column)
            sheet.column_dimensions[column[0].column_letter].width = length + 2
print('\nData saved into Excel file!')