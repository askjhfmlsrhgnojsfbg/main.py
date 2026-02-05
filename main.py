import os
import requests
import pandas as pd
import time

# LẤY API KEY: Phải dùng đúng chữ "SERPAPI_KEY"
API_KEY = os.getenv("SERPAPI_KEY") 
SEARCH_QUERY = "Thác Dải Yếm"
MAX_PAGES = 5 

def get_reviews():
    if not API_KEY:
        print("LỖI: Không tìm thấy API Key trong Secrets!")
        return

    print(f"--- Đang lấy dữ liệu cho: {SEARCH_QUERY} ---")
    search_params = {"engine": "google_maps", "q": SEARCH_QUERY, "api_key": API_KEY, "hl": "vi"}
    
    try:
        search_data = requests.get("https://serpapi.com/search", params=search_params).json()
        data_id = search_data.get("place_results", {}).get("data_id") or search_data.get("local_results", [{}])[0].get("data_id")

        if not data_id:
            print("Không tìm thấy mã địa điểm!")
            return

        all_reviews = []
        next_page_token = None

        for page in range(MAX_PAGES):
            print(f"Đang lấy trang {page + 1}...")
            review_params = {
                "engine": "google_maps_reviews",
                "data_id": data_id,
                "api_key": API_KEY,
                "hl": "vi",
                "next_page_token": next_page_token
            }
            response = requests.get("https://serpapi.com/search", params=review_params).json()
            current_reviews = response.get("reviews", [])
            if not current_reviews: break
            all_reviews.extend(current_reviews)
            next_page_token = response.get("serpapi_pagination", {}).get("next_page_token")
            if not next_page_token: break
            time.sleep(1)

        if all_reviews:
            df = pd.DataFrame(all_reviews)
            # Chỉ lấy các cột quan trọng
            cols = [c for c in ['user', 'rating', 'snippet', 'date'] if c in df.columns]
            df[cols].to_excel("du_lieu_binh_luan.xlsx", index=False)
            print(f"Xong! Đã lấy {len(all_reviews)} bình luận.")
    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == "__main__":
    get_reviews()
    
