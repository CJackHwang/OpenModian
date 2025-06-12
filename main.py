# -*- coding: utf-8 -*-
import random
import re  # 正则表达式，进行文字匹配
import socket
import time
import urllib.error  # 制定URL，获取网页数据
import urllib.request
import requests
import xlwt  # 进行excel操作
from bs4 import BeautifulSoup  # 网页解析，获取数据
from openpyxl import Workbook
from openpyxl.utils.exceptions import IllegalCharacterError
import datetime

# 正则表达式 (仅保留非HTML解析用途的)
find_trueauthorid = re.compile(r'https://me.modian.com/u/detail\?uid=(\d+)')
find_linkid_re = re.compile(r'https://zhongchou.modian.com/item/(\d+).html')

# 储存路径
savepath = "摩点众筹-主要信息.xls"

# 可分类爬取 (保持不变，但主逻辑会先处理 all)
baseurl_list = [
    # "https://zhongchou.modian.com/all/top_time/success/",
    # "https://zhongchou.modian.com/all/top_time/going/",
    # "https://zhongchou.modian.com/all/top_time/preheat/",
    "https://zhongchou.modian.com/all/top_time/idea/"
]

def askURL(url):
    head = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    timeout_range = (10, 20)

    # Create SSL context that's more permissive
    import ssl
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    html = ""
    for i in range(5):  # Increased retry attempts
        try:
            timeout = random.randint(*timeout_range)
            request = urllib.request.Request(url, headers=head)
            response = urllib.request.urlopen(request, timeout=timeout, context=ssl_context)
            html = response.read().decode("utf-8")
            break
        except (urllib.error.URLError, ConnectionResetError, socket.timeout, ssl.SSLError) as e:
            print(f'第{i + 1}次尝试失败，原因：{e} URL: {url}')
            if i == 4:  # Last attempt
                print(f'重试多次仍然失败！URL: {url}')
                break
            # Exponential backoff
            wait_time = (i + 1) * 2
            print(f'等待 {wait_time} 秒后重试...')
            time.sleep(wait_time)
    return html

def askURL2(url): # For author pages
    head = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1'
    }
    timeout_range = (10, 20)

    # Create SSL context that's more permissive
    import ssl
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    html = ""
    for i in range(5):  # Increased retry attempts
        try:
            timeout = random.randint(*timeout_range)
            request = urllib.request.Request(url, headers=head)
            response = urllib.request.urlopen(request, timeout=timeout, context=ssl_context)
            html = response.read().decode("utf-8")
            break
        except (urllib.error.URLError, ConnectionResetError, socket.timeout, ssl.SSLError) as e:
            print(f'第{i + 1}次尝试(askURL2)失败，原因：{e} URL: {url}')
            if i == 4:  # Last attempt
                print(f'重试多次(askURL2)仍然失败！URL: {url}')
                break
            # Exponential backoff
            wait_time = (i + 1) * 2
            print(f'等待 {wait_time} 秒后重试...')
            time.sleep(wait_time)
    return html


def get_author_info_from_api(uid):
    home_url = "https://apim.modian.com/apis/comm/user/user_info"
    params = {"json_type": 1, "to_user_id": uid, "user_id": uid}
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Mobile Safari/537.36',
        'Origin': 'https://m.modian.com',
        'Referer': 'https://m.modian.com/',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Timestamp': str(int(time.time()))
    }
    try:
        response = requests.get(home_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching author API for UID {uid}: {e}")
        return {}


def parse_author_page_info(html, author_id_from_url):
    soup = BeautifulSoup(html, "html.parser")
    author_data = []

    fans_num = 0
    notice_number = 0
    love_number = 0

    banner_div = soup.find('div', {'class': 'banner'})
    if banner_div:
        cont_div = banner_div.find('div', {'class': 'cont'})
        if cont_div:
            fans_span = cont_div.find('span', {'class': 'go_span fans'})
            if fans_span and fans_span.find('i'):
                fans_num_text = fans_span.find('i').text.strip()
                if fans_num_text.isdigit():
                    fans_num = int(fans_num_text)

            notice_span = cont_div.select_one('span.go_span:not(.fans)')
            if notice_span:
                text = notice_span.text.strip()
                parts = text.split()
                if parts and parts[0].isdigit():
                    notice_number = int(parts[0])

            all_span = cont_div.find('span', {'id': 'ALL'})
            if all_span:
                text2 = all_span.text.strip()
                parts2 = text2.split()
                if parts2 and parts2[0].isdigit():
                    love_number = int(parts2[0])
    
    author_data.extend([fans_num, notice_number, love_number])

    detail_result = {}
    detail_div = soup.find('div', {'class': 'detail'})
    if detail_div:
        for item_div in detail_div.find_all('div', class_='item'):
            label_tag = item_div.find('label')
            p_tag = item_div.find('p')
            if label_tag and p_tag:
                detail_result[label_tag.text.strip()] = p_tag.text.strip()
    author_data.append(str(detail_result))

    other_result = {}
    other_info_div = soup.find('div', {'class': 'other_info'})
    if other_info_div:
        for item_div in other_info_div.find_all('div', class_='item'):
            p_tags = item_div.find_all('p')
            if len(p_tags) == 2 and p_tags[1].text.strip().isdigit():
                value = int(p_tags[1].text.strip())
                key = p_tags[0].text.strip()
                other_result[key] = value
    author_data.append(str(other_result))
    
    userhome_url = f"https://m.modian.com/user/homePage/{author_id_from_url}"
    author_data.append(userhome_url)
    
    return author_data


def get_project_status_info(soup_detail_page):
    status_info = {
        "item_class": "未知情况",
        "is_idea": False,
        "is_preheat": False,
        "is_going": False,
        "is_success": False,
        "is_fail": False # Added for clarity
    }
    buttons_div = soup_detail_page.find('div', {'class': 'buttons clearfloat'})
    if buttons_div:
        button_a = buttons_div.select_one('a')
        if button_a:
            class_result_text = button_a.text.strip()
            status_info["raw_status_text"] = class_result_text # Store raw text for debugging
            if class_result_text == "看好":
                status_info["item_class"] = "创意"
                status_info["is_idea"] = True
            elif class_result_text == "看好项目":
                status_info["item_class"] = "预热"
                status_info["is_preheat"] = True
            elif class_result_text == "立即购买支持":
                status_info["item_class"] = "众筹中"
                status_info["is_going"] = True
            elif class_result_text == "众筹成功":
                status_info["item_class"] = "众筹成功"
                status_info["is_success"] = True
            elif class_result_text == "项目终止":
                status_info["item_class"] = "项目终止" # Often implies success or specific end state
                status_info["is_success"] = True # Or a different flag if needed
            elif class_result_text == "众筹结束": # This usually means failed if not successful
                status_info["item_class"] = "众筹失败"
                status_info["is_fail"] = True
                status_info["is_going"] = True # Was likely 'going' before ending as fail
            elif class_result_text == "众筹取消":
                status_info["item_class"] = "众筹取消"
                status_info["is_fail"] = True # Or a different flag
                status_info["is_going"] = True # Was likely 'going' before cancel
    return status_info

def parse_upper_items(soup_detail_page, project_status):
    data = []
    starttime = "none"
    endtime = "none"
    itemreal_class = project_status["item_class"]

    if project_status["is_preheat"]:
        start_time_div = soup_detail_page.find('div', {'class': 'col2 start-time'})
        if start_time_div:
            h3_tags = start_time_div.find_all('h3')
            if len(h3_tags) > 0 and h3_tags[0]:
                 starttime = h3_tags[0].text.strip() # "YYYY-MM-DD HH:MM 开始"
                 if "开始" in starttime: starttime = starttime.replace("开始","").strip()

            if len(h3_tags) > 1 and h3_tags[1]: # This might be end time or other info
                endtime_text_candidate = h3_tags[1].text.strip()
                if "结束" in endtime_text_candidate: # "YYYY-MM-DD HH:MM 结束"
                    endtime = endtime_text_candidate.replace("结束","").strip()
                else: # If not explicitly "结束", it's likely still preheating
                    endtime = "预热中"
            else:
                endtime = "预热中"

            if starttime != "none" and starttime != "预热中":
                try:
                    now = datetime.datetime.now()
                    starttime_std = datetime.datetime.strptime(starttime, "%Y-%m-%d %H:%M")
                    if starttime_std < now: # If preheat start time has passed, it should be 'going'
                        itemreal_class = "众筹中" # Override class
                        endtime = "众筹中—预热异常转众筹中" # Mark as special case
                        # Update project_status accordingly if this function could modify it
                        # For now, just local itemreal_class for this data point
                except ValueError:
                    pass # Keep original starttime if format is unexpected
    elif project_status["is_idea"]:
        starttime = "创意中"
        endtime = "创意中"
    else: # Going, Success, Fail
        remain_time_div = soup_detail_page.find('div', {'class': 'col2 remain-time'})
        if remain_time_div:
            h3_tags = remain_time_div.find_all('h3')
            if len(h3_tags) > 0 and h3_tags[0] and h3_tags[0].get('start_time'):
                starttime = h3_tags[0].get('start_time')
            if len(h3_tags) > 0 and h3_tags[0] and h3_tags[0].get('end_time'): # Sometimes end_time is on the first h3
                 endtime = h3_tags[0].get('end_time')
            elif len(h3_tags) > 1 and h3_tags[1] and h3_tags[1].get('end_time'): # More commonly on the second
                 endtime = h3_tags[1].get('end_time')


    data.extend([starttime, endtime, itemreal_class])

    sponsor_info_div = soup_detail_page.find('div', {'class': 'sponsor-info clearfix'})
    sponsor_href = "none"
    true_authorid_from_re = "none"
    author_image = "none"
    category = "none"
    author_name = "none"
    author_uid_attr = "0" # data-username
    parsed_author_page_details = ["0", "0", "0", "{}", "{}", "none"] # Defaults for fans, notice, love, etc.

    if sponsor_info_div:
        sponsor_link_tag = sponsor_info_div.find('a', {'class': 'sponsor-link'})
        if sponsor_link_tag and sponsor_link_tag.get('href'):
            sponsor_href = sponsor_link_tag.get('href')
            match_id = find_trueauthorid.search(sponsor_href)
            if match_id:
                true_authorid_from_re = match_id.group(1)
                # Fetch and parse author's own page
                author_page_html = askURL2(sponsor_href) # Use askURL2 for m.modian.com
                if author_page_html:
                    parsed_author_page_details = parse_author_page_info(author_page_html, true_authorid_from_re)

        img_tag = sponsor_info_div.find('img', {'class': 'sponsor-image'})
        if img_tag and img_tag.get('src'):
            author_image = img_tag.get('src')

        category_span = sponsor_info_div.find('span', string=re.compile(r'项目类别：'))
        if category_span:
            category = category_span.text.replace('项目类别：', '').strip()

        name_span = sponsor_info_div.find('span', {'class': 'name'})
        if name_span:
            author_name = name_span.get('data-nickname', name_span.text.strip())
            author_uid_attr = name_span.get('data-username', "0")


    data.append(sponsor_href) # User homepage link
    data.append(author_image)
    data.append(category)
    data.append(author_name)
    data.append(author_uid_attr) # This is the one from data-username, often the same as true_authorid_from_re

    # Project base info (money, percent, goal, sponsor_num)
    money = "0"
    percent = "0"
    goal_money = "0"
    sponsor_num = "0"

    if project_status["is_preheat"]:
        center_div = soup_detail_page.find('div', {'class': 'center'})
        if center_div:
            goal_div = center_div.find('div', {'class': 'col1 project-goal'})
            if goal_div and goal_div.find('h3') and goal_div.find('h3').find('span'):
                goal_money = goal_div.find('h3').find('span').text.strip().replace('￥', '')
            
            subscribe_span = center_div.find('span', {'subscribe_count': True})
            if subscribe_span:
                sponsor_num = subscribe_span.text.strip().replace('人订阅', '') # "人订阅" or just number
                if not sponsor_num.isdigit() and subscribe_span.get('subscribe_count'): # Fallback to attribute
                    sponsor_num = subscribe_span.get('subscribe_count', "0")


    elif project_status["is_idea"]:
        goal_money = 'none' # No goal in idea phase typically
        sponsor_num = 'none' # No sponsors, but maybe "likes" - see main_middle
    else: # Going, Success, Fail
        center_div = soup_detail_page.find('div', {'class': 'center'})
        if center_div:
            money_span = center_div.find('span', {'backer_money': True})
            if money_span:
                money = money_span.text.strip().replace('￥', '')
            
            rate_span = center_div.find('span', {'rate': True})
            if rate_span:
                percent = rate_span.text.strip().replace('%', '')

            goal_span = center_div.find('span', {'class': 'goal-money'})
            if goal_span:
                goal_money = goal_span.text.strip().replace('目标金额 ', '').replace('￥', '')
            
            backer_span = center_div.find('span', {'backer_count': True})
            if backer_span:
                sponsor_num = backer_span.text.strip().replace('人支持', '') # "人支持" or just number
                if not sponsor_num.isdigit() and backer_span.get('backer_count'): # Fallback
                    sponsor_num = backer_span.get('backer_count', "0")


    data.extend([money, percent, goal_money, sponsor_num])
    data.append(true_authorid_from_re) # The ID extracted from sponsor_href
    data.extend(parsed_author_page_details) # fans_num, notice_number, love_number, detail_result_str, other_result_str, userhome_url_confirmation
    return data


def parse_main_left_content(soup_detail_page):
    data = []
    img_list = []
    video_list = []
    main_left_div = soup_detail_page.find('div', {'class': 'main-left'})
    if main_left_div:
        project_content_div = main_left_div.find('div', {'class': 'project-content'})
        if project_content_div:
            for img_tag in project_content_div.find_all('img'):
                if img_tag.get('src'):
                    img_list.append(img_tag.get('src'))
            for video_tag in project_content_div.find_all('video'):
                if video_tag.get('src'): # Direct src attribute
                    video_list.append(video_tag.get('src'))
                else: # Check for source tags
                    for source_tag in video_tag.find_all('source'):
                        if source_tag.get('src'):
                            video_list.append(source_tag.get('src'))
                            break # Usually one source is enough
    data.extend([len(img_list), str(img_list), len(video_list), str(video_list)])
    return data

def parse_main_right_rewards(soup_detail_page):
    rewards_data_list_str = [] # List of strings, each representing a reward tier
    main_right_div = soup_detail_page.find('div', {'class': 'main-right'})
    if main_right_div:
        payback_lists_div = main_right_div.find('div', {'class': 'payback-lists margin36'})
        if payback_lists_div:
            for reward_item_div in payback_lists_div.find_all('div', class_=lambda x: x and 'back-list' in x):
                single_reward_details = []
                
                back_money = "0"
                head_div = reward_item_div.find('div', {'class': 'head'})
                if head_div and head_div.find('span'):
                    back_money_text = head_div.find('span').text.strip().replace('￥','')
                    if back_money_text.isdigit(): back_money = back_money_text
                
                backsponsor = "0"
                if head_div and head_div.find('em'):
                    em_text = head_div.find('em').text.strip() # e.g., "23 人支持" or "已满"
                    parts = em_text.split()
                    if parts and parts[0].isdigit(): backsponsor = parts[0]
                    elif "已满" in em_text: backsponsor = "已满"


                sign_logo = "0" # Default, might be "限量" or number
                zc_subhead_div = reward_item_div.find('div', {'class': 'zc-subhead'})
                if zc_subhead_div and zc_subhead_div.find('span'):
                    sign_logo_text = zc_subhead_div.find('span').text.strip()
                    if "限量" in sign_logo_text:
                        num_part = sign_logo_text.replace("限量","").replace("份","").strip()
                        sign_logo = f"限量 {num_part}" if num_part.isdigit() else "限量"
                    elif sign_logo_text.isdigit(): # Unlikely based on old regex, but good to check
                        sign_logo = sign_logo_text


                backtitle = "none"
                backtext = "none"
                backtime = "none"
                
                back_content_div = reward_item_div.find('div', {'class': 'back-content'})
                if back_content_div:
                    title_div = back_content_div.find('div', {'class': 'back-sub-title'})
                    if title_div: backtitle = title_div.text.strip()
                    
                    detail_div = back_content_div.find('div', {'class': 'back-detail'})
                    if detail_div: backtext = detail_div.text.strip()
                    
                    time_div = back_content_div.find('div', {'class': 'back-time'})
                    if time_div: backtime = time_div.text.strip()

                single_reward_details.extend([backtitle, sign_logo, back_money, backsponsor, backtime, backtext])
                rewards_data_list_str.append(str(single_reward_details))
                
    return [str(rewards_data_list_str), len(rewards_data_list_str)]


def parse_main_middle_nav_info(soup_detail_page, project_status):
    data = []
    update_number = "0"
    comment_number = "0"
    userlist_num = "0" # Supporters for going/success, Likes for idea
    collect_number = "0" # Attention/collection

    nav_wrap_inner = soup_detail_page.find('div', {'class': 'nav-wrap-inner'})
    if nav_wrap_inner:
        nav_left = nav_wrap_inner.find('ul', {'class': 'nav-left'})
        if nav_left:
            update_li = nav_left.find('li', {'class': 'pro-gengxin'})
            if update_li and update_li.find('span', {'upadte_count': True}): # Corrected typo from upadte to update
                 update_number = update_li.find('span', {'upadte_count': True}).text.strip()
            elif update_li and update_li.find('span'): # Fallback if attribute name is different
                 update_number = update_li.find('span').text.strip()


            comment_li = nav_left.find('li', {'class': 'nav-comment'})
            if comment_li and comment_li.find('span', {'comment_count': True}):
                comment_number = comment_li.find('span', {'comment_count': True}).text.strip()
            elif comment_li and comment_li.find('span'):
                 comment_number = comment_li.find('span').text.strip()


            userlist_li = nav_left.find('li', class_='dialog_user_list') # Support/Like count
            if userlist_li:
                span_tag = None
                if project_status["is_idea"]:
                    span_tag = userlist_li.find('span', {'bull_count': True}) # Likes for idea
                else:
                    span_tag = userlist_li.find('span', {'backer_count': True}) # Supporters for others
                
                if span_tag:
                    userlist_num = span_tag.text.strip()
                elif userlist_li.find('span'): # Fallback
                    userlist_num = userlist_li.find('span').text.strip()


        if not project_status["is_idea"]: # Collect/Attention is usually not for idea phase or different
            nav_right = nav_wrap_inner.find('ul', {'class': 'nav-right'})
            if nav_right:
                atten_li = nav_right.find('li', {'class': 'atten'})
                if atten_li and atten_li.find('span'):
                    collect_number = atten_li.find('span').text.strip()
        else: # For idea phase, "collect_number" might be the same as "userlist_num" (likes)
            collect_number = userlist_num


    # Ensure numbers are digits or "0"
    update_number = update_number if update_number.isdigit() else "0"
    comment_number = comment_number if comment_number.isdigit() else "0"
    userlist_num = userlist_num if userlist_num.isdigit() else "0"
    collect_number = collect_number if collect_number.isdigit() else "0"
    
    data.extend([update_number, comment_number, userlist_num, collect_number])
    return data


def parse_project_detail_page(html_content):
    """Parses the detailed project page."""
    soup = BeautifulSoup(html_content, "html.parser")
    project_data = []

    project_status = get_project_status_info(soup)
    
    # Upper items: time, author, basic funding info
    upper_items_data = parse_upper_items(soup, project_status)
    project_data.extend(upper_items_data)

    # Right items: Rewards
    main_right_data = parse_main_right_rewards(soup)
    project_data.extend(main_right_data)

    # Middle items: Nav counts (updates, comments, supporters/likes, collections)
    main_middle_data = parse_main_middle_nav_info(soup, project_status)
    project_data.extend(main_middle_data)
    
    # Left items: Project content images/videos
    main_left_data = parse_main_left_content(soup)
    project_data.extend(main_left_data)
    
    return project_data


def parse_main_listing_page(html_content, current_excel_index_ref):
    """Parses the main listing page (e.g., /all/top_time/all/1) for project items."""
    soup = BeautifulSoup(html_content, "html.parser")
    datalist_batch = []

    pro_field_div = soup.find('div', {'class': 'pro_field'})
    if not pro_field_div:
        print("No 'pro_field' div found on listing page.")
        return datalist_batch, current_excel_index_ref

    # Find all project items - they are in <li> elements within the pro_field div
    project_items = pro_field_div.find_all('li')
    if not project_items:
        print("No project items found in pro_field div.")
        return datalist_batch, current_excel_index_ref

    for item_li in project_items:
        current_excel_index_ref += 1 # Increment shared index
        single_project_base_data = [current_excel_index_ref] # Start with new auto-incremented index

        # Find the project link - look for any <a> tag with href containing "/item/"
        link_tag = None
        item_link = "none"
        item_id = ""

        # Try to find the main project link
        for a_tag in item_li.find_all('a'):
            href = a_tag.get('href', '')
            if '/item/' in href:
                link_tag = a_tag
                item_link = href
                break

        if link_tag and item_link != "none":
            if not item_link.startswith("http"):
                item_link = "https://zhongchou.modian.com" + item_link

            id_match = find_linkid_re.search(item_link)
            if id_match:
                item_id = id_match.group(1)

        single_project_base_data.append(item_link)
        single_project_base_data.append(item_id)

        # Find the project title
        title = "none"
        title_h3 = item_li.find('h3', class_='pro_title')
        if title_h3:
            title = title_h3.text.strip()
        elif link_tag and link_tag.text:
            title = link_tag.text.strip()

        # Skip specific items as per original logic
        if "可汗游戏大会" in title:
            current_excel_index_ref -= 1 # Decrement back as we are skipping
            continue

        single_project_base_data.append(title)

        # Find the project image
        img_src = "none"
        img_tag = item_li.find('img')
        if img_tag and img_tag.get('src'):
            img_src = img_tag.get('src')
        single_project_base_data.append(img_src)

        print(f"Processing: {current_excel_index_ref} - {title} ({item_link})")

        # Fetch and parse detail page
        if item_link != "none" and item_id: # Only proceed if we have a valid link/ID
            detail_page_html = askURL(item_link)
            if detail_page_html:
                detail_page_data = parse_project_detail_page(detail_page_html)
                single_project_base_data.extend(detail_page_data)
            else:
                print(f"Failed to fetch detail page for {item_link}")
                # Add placeholders for detail_data if fetch fails, to maintain column consistency
                # Number of placeholders should match expected fields from parse_project_detail_page
                # upper (11) + right (2) + middle (4) + left (4) = 21 placeholders
                single_project_base_data.extend(["error_fetching_details"] * 21)
        else:
            print(f"Skipping detail fetch for item without link/ID: {title}")
            single_project_base_data.extend(["no_link_for_details"] * 21)

        datalist_batch.append(single_project_base_data)

    return datalist_batch, current_excel_index_ref

def save_data_to_excel(workbook, sheet, data_rows_list, start_row_idx):
    """Saves a list of data rows to the excel sheet."""
    print(f"Saving {len(data_rows_list)} rows to Excel, starting at sheet row {start_row_idx + 1}...")

    col_headers = (
        "序号", "项目link", "项目6位id", "项目名称", "项目图",  # Base info from listing (5)
        "开始时间", "结束时间", "项目结果",  # from upper (3)
        "用户主页(链接)", "用户头像(图片链接)", "分类", "用户名", "用户UID(data-username)", # from upper (5)
        "已筹金额", "百分比", "目标金额", "支持者(数量)", # from upper (4)
        "真实用户ID(链接提取)", "作者页-粉丝数", "作者页-关注数", "作者页-获赞数", "作者页-详情", "作者页-其他信息", "作者页-主页确认", # from upper's author parse (7)
        "回报列表信息(字符串)", "回报列表项目数",  # from right (2)
        "项目更新数", "评论数", "项目支持者/点赞数", "收藏数",  # from middle (4)
        "项目详情-图片数量", "项目详情-图片(列表字符串)", "项目详情-视频数量", "项目详情-视频(列表字符串)"  # from left (4)
    ) # Total 34 columns

    # Write headers only once
    if start_row_idx == 0:
        for i, header_name in enumerate(col_headers):
            sheet.write(0, i, header_name)

    # Process each row of data
    for row_idx, row_data in enumerate(data_rows_list):
        if not row_data:
            continue

        # Calculate the actual Excel row number
        excel_row_num = start_row_idx + row_idx + 1  # +1 because headers are at row 0

        # Ensure row_data is a list and has enough elements
        if not isinstance(row_data, list):
            row_data = list(row_data) if hasattr(row_data, '__iter__') else [row_data]

        # Pad with empty strings if not enough columns
        padded_row_data = row_data + [""] * (len(col_headers) - len(row_data))

        # Write each cell in the row
        for col_idx, cell_value in enumerate(padded_row_data):
            cell_str = str(cell_value) if cell_value is not None else ""

            # Handle Excel cell character limit
            if len(cell_str) > 32767:
                cell_str = cell_str[:32767] + "...TRUNCATED"

            try:
                sheet.write(excel_row_num, col_idx, cell_str)
            except Exception as e:
                print(f"Error writing to Excel cell ({excel_row_num},{col_idx}): {e}. Value: {cell_str[:50]}")
                try:
                    sheet.write(excel_row_num, col_idx, "ERROR_WRITING_CELL")
                except:
                    pass  # Skip if even error message can't be written

    # Save the workbook
    try:
        workbook.save(savepath)
        print(f"Data saved to {savepath}")
    except Exception as e:
        print(f"Error saving workbook: {e}")


def run_scraper():
    main_workbook = xlwt.Workbook(encoding="utf-8", style_compression=0)
    main_sheet = main_workbook.add_sheet('all_projects', cell_overwrite_ok=True)
    
    # Shared list for excel index, passed by reference (as a list) to parsing function
    # excel_index_counter will be the global running index for rows in Excel
    excel_index_counter = 0 # Start at 0 because headers are row 0, data starts at row 1

    # Write headers first
    save_data_to_excel(main_workbook, main_sheet, [], 0) # Pass empty data list to just write headers

    # For now, focusing on the "all" URL as in the original main() call
    base_crawl_url = "https://zhongchou.modian.com/all/top_time/all/"
    
    total_projects_processed = 0
    # Original loop was range(1, 833). Use a smaller range for testing.
    # For full run, change back to 833 or determine dynamically.
    for page_num in range(1, 3): # DEBUG: Reduced page range
        print(f"\n--- Scraping Page {page_num} ---")
        current_page_url = base_crawl_url + str(page_num)
        page_html = askURL(current_page_url)

        if not page_html:
            print(f"Failed to get HTML for page {page_num}. Skipping.")
            continue

        # excel_index_counter is passed and its 0-th element is modified by parse_main_listing_page
        projects_on_page, excel_index_counter = parse_main_listing_page(page_html, excel_index_counter)
        
        if projects_on_page:
            # The excel_index_counter is already the latest global index.
            # The first element of each project_data in projects_on_page IS this global index.
            # So, we don't need a separate start_row_idx for save_data_to_excel if data is written one by one
            # or if the list contains the correct global index.
            # Let's save after each page for now.
            save_data_to_excel(main_workbook, main_sheet, projects_on_page, 0) # start_row_idx 0 means headers are at 0
            total_projects_processed += len(projects_on_page)
            print(f"Processed {len(projects_on_page)} projects from page {page_num}. Total processed: {total_projects_processed}")
        else:
            print(f"No projects found or processed on page {page_num}.")
            # Consider breaking if no projects found on a page, might be end of listings
            # break 

        # Optional: Save workbook more frequently if needed (e.g. every N pages)
        if page_num % 5 == 0: # Save every 5 pages
             print(f"Intermediate save at page {page_num}...")
             main_workbook.save(savepath)


    print(f"\n--- Scraping Finished ---")
    print(f"Total projects processed and attempted to save: {total_projects_processed}")
    print(f"Final global excel row index reached: {excel_index_counter}")
    main_workbook.save(savepath) # Final save
    print(f"All data saved to {savepath}")


if __name__ == "__main__":
    run_scraper()
    print("爬取完毕！")
