import os
import requests
import pandas as pd
import time

# 1. LẤY API KEY TỪ HỆ THỐNG BẢO MẬT CỦA GITHUB
API_KEY = os.getenv("e92056bfd79151633a516cbe91c9f91afb54f8994cb4b70c9c7079b9f9c16fd1") 
SEARCH_QUERY = "Thác Dải Yếm"
MAX_PAGES = 3 # Lấy khoảng 30 bình luận mỗi lần chạy để tiết kiệm lượt dùng

def get_reviews():
    # Bước A: Tìm data_id
    search_params = {"engine": "google_maps", "q": SEARCH_QUERY, "api_key": API_KEY, "hl": "vi"}
    search_data = requests.get("https://serpapi.com/search", params=search_params).json()
    data_id = search_data.get("place_results", {}).get("data_id") or search_data.get("local_results", [{}])[0].get("data_id")

    if not data_id:
        print("Không tìm thấy địa điểm!")
        return

    all_reviews = []
    next_page_token = None

    # Bước B: Vòng lặp lấy nhiều trang
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

    # Bước C: Lưu vào file Excel (Robot GitHub sẽ tự thấy file này để lưu lại)
    if all_reviews:
        df = pd.DataFrame(all_reviews)
        df_final = df[['user', 'rating', 'snippet', 'date']]
        file_name = "du_lieu_binh_luan.xlsx"
        df_final.to_excel(file_name, index=False)
        print(f"Đã lưu {len(all_reviews)} bình luận vào {file_name}")

if __name__ == "__main__":
    get_reviews()
