import requests
import csv

# Fixed access token
PAGE_ACCESS_TOKEN = "EAAVChJmQ8fgBPCy2cxYMCuPgAn24q8kNNjzV9wKpKvnkFEFAWHY0AS8laDZBvWXD5Yc5lW3wHboFcc58V83wsELavxbkAZBKKfkfpIi55CzMzNWc05czkRvBvAdAuYcRAbWWYVr2lkkGCouyhoqTe2C4Ivv5OlWolHz2sAj9aS0ZCdmxAZBu790YxNyOpz0TBZBlEznaLX7C7eXqVkZCXejiH8ZBPVPaASUZAAFyJ2GgXQZDZD"
OUTPUT_CSV = "facebook_page_data.csv"

def get_page_id(page_name, access_token):
    url = f"https://graph.facebook.com/v17.0/{page_name}"
    params = {"access_token": access_token, "fields": "id"}
    response = requests.get(url, params=params).json()
    if "error" in response:
        print("Facebook API Error (Get Page ID):", response["error"])
        return None
    return response.get("id")

def get_page_details(page_id, access_token):
    url = f"https://graph.facebook.com/v17.0/{page_id}"
    params = {
        "access_token": access_token,
        "fields": "name,category,location,phone,about"
    }
    response = requests.get(url, params=params).json()
    if "error" in response:
        print("Facebook API Error (Page Details):", response["error"])
        return {}

    location = response.get("location", {})
    # Combine all location fields into one string
    address = ", ".join(filter(None, [
        location.get("street"),
        location.get("city"),
        location.get("state"),
        location.get("zip"),
        location.get("country")
    ]))

    return {
        "name": response.get("name", ""),
        "category": response.get("category", ""),
        "address": address,
        "phone": response.get("phone", ""),
        "about": response.get("about", "")
    }


def get_page_reviews(page_id, access_token):
    reviews = []
    url = f"https://graph.facebook.com/v17.0/{page_id}/ratings"
    params = {"access_token": access_token, "fields": "reviewer,rating,review_text,created_time"}
    while url:
        response = requests.get(url, params=params).json()
        if "error" in response:
            print("Facebook API Error (Reviews):", response["error"])
            break
        reviews.extend(response.get("data", []))
        url = response.get("paging", {}).get("next")
        params = None
    return reviews

def get_page_posts(page_id, access_token):
    posts = []
    url = f"https://graph.facebook.com/v17.0/{page_id}/posts"
    params = {
        "access_token": access_token,
        "fields": "id,message,created_time,permalink_url,likes.summary(true),comments{message,from,created_time}"
    }
    while url:
        response = requests.get(url, params=params).json()
        if "error" in response:
            print("Facebook API Error (Posts):", response["error"])
            break
        posts.extend(response.get("data", []))
        url = response.get("paging", {}).get("next")
        params = None
    return posts

def save_to_csv(page_info, reviews, posts, filename):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Header
        writer.writerow([
            "Business Name","Category","Address","Phone",
            "Post ID","Post Message","Post Time","Post URL","Likes Count",
            "Comment ID","Commenter Name","Comment Message","Comment Time",
            "Review ID","Reviewer Name","Rating","Review Text","Review Time"
        ])
        
        max_len = max(len(posts), len(reviews))
        for i in range(max_len):
            post = posts[i] if i < len(posts) else {}
            comments = post.get("comments", {}).get("data", []) if post else []
            
            if comments:
                for comment in comments:
                    review = reviews[i] if i < len(reviews) else {}
                    writer.writerow([
                        page_info.get("name", ""),
                        page_info.get("category", ""),
                        page_info.get("address", ""),
                        page_info.get("phone", ""),
                        post.get("id",""),
                        post.get("message",""),
                        post.get("created_time",""),
                        post.get("permalink_url",""),
                        post.get("likes", {}).get("summary", {}).get("total_count",0),
                        comment.get("id",""),
                        comment.get("from", {}).get("name",""),
                        comment.get("message",""),
                        comment.get("created_time",""),
                        review.get("id",""),
                        review.get("reviewer", {}).get("name",""),
                        review.get("rating",""),
                        review.get("review_text",""),
                        review.get("created_time","")
                    ])
            else:
                review = reviews[i] if i < len(reviews) else {}
                writer.writerow([
                    page_info.get("name", ""),
                    page_info.get("category", ""),
                    page_info.get("address", ""),
                    page_info.get("phone", ""),
                    post.get("id","") if post else "",
                    post.get("message","") if post else "",
                    post.get("created_time","") if post else "",
                    post.get("permalink_url","") if post else "",
                    post.get("likes", {}).get("summary", {}).get("total_count",0) if post else 0,
                    "","","","",
                    review.get("id",""),
                    review.get("reviewer", {}).get("name",""),
                    review.get("rating",""),
                    review.get("review_text",""),
                    review.get("created_time","")
                ])

if __name__ == "__main__":
    page_name = input("Enter Facebook Page Name/Username: ").strip()
    print("Fetching Page ID...")
    page_id = get_page_id(page_name, PAGE_ACCESS_TOKEN)
    if not page_id:
        print("❌ Could not fetch Page ID. Exiting.")
    else:
        print("Fetching page details...")
        page_info = get_page_details(page_id, PAGE_ACCESS_TOKEN)
        
        print("Fetching reviews...")
        reviews = get_page_reviews(page_id, PAGE_ACCESS_TOKEN)
        
        print("Fetching posts and comments...")
        posts = get_page_posts(page_id, PAGE_ACCESS_TOKEN)
        
        print("Saving all data to CSV...")
        save_to_csv(page_info, reviews, posts, OUTPUT_CSV)
        print(f"✅ Data saved to {OUTPUT_CSV}")
