import requests
import pandas as pd
import time # Để dừng nghỉ giữa các lần lấy, tránh bị khóa
from google.colab import files

# ======================================================
# CẤU HÌNH
# ======================================================
API_KEY = "e92056bfd79151633a516cbe91c9f91afb54f8994cb4b70c9c7079b9f9c16fd1"
SEARCH_QUERY = "Thác Dải Yếm"
MAX_PAGES = 5 # Bạn muốn lấy bao nhiêu trang? (Mỗi trang ~10 bình luận)

# ======================================================
# BƯỚC 1: LẤY DATA_ID CỦA ĐỊA ĐIỂM (Giống code cũ)
# ======================================================
search_params = {"engine": "google_maps", "q": SEARCH_QUERY, "api_key": API_KEY, "hl": "vi"}
search_data = requests.get("https://serpapi.com/search", params=search_params).json()
data_id = search_data.get("place_results", {}).get("data_id") or search_data.get("local_results", [{}])[0].get("data_id")

if not data_id:
    print("Không tìm thấy mã địa điểm!")
else:
    all_reviews = []
    next_page_token = None # Token để nhảy sang trang tiếp theo

    print(f"--- Bắt đầu lấy bình luận cho {SEARCH_QUERY} ---")

    # ======================================================
    # BƯỚC 2: VÒNG LẶP LẤY NHIỀU TRANG
    # ======================================================
    for page in range(MAX_PAGES):
        print(f"Đang lấy dữ liệu trang {page + 1}...")
        
        review_params = {
            "engine": "google_maps_reviews",
            "data_id": data_id,
            "api_key": API_KEY,
            "hl": "vi",
            "next_page_token": next_page_token # Gửi token của trang trước để lấy trang sau
        }
        
        response = requests.get("https://serpapi.com/search", params=review_params).json()
        current_reviews = response.get("reviews", [])
        
        if not current_reviews:
            print("Đã hết bình luận để lấy.")
            break
            
        all_reviews.extend(current_reviews) # Gộp bình luận mới vào danh sách tổng
        
        # Kiểm tra xem có trang tiếp theo không
        next_page_token = response.get("serpapi_pagination", {}).get("next_page_token")
        
        if not next_page_token:
            print("Đây là trang cuối cùng.")
            break
            
        time.sleep(1) # Nghỉ 1 giây để server không bị quá tải

    # ======================================================
    # BƯỚC 3: XUẤT FILE EXCEL
    # ======================================================
    if all_reviews:
        df = pd.DataFrame(all_reviews)
        # Lọc các cột quan trọng
        df_final = df[['user', 'rating', 'snippet', 'date']]
        file_name = f"full_binh_luan_{SEARCH_QUERY.replace(' ', '_')}.xlsx"
        df_final.to_excel(file_name, index=False)
        
        print(f"\n✓ THÀNH CÔNG! Đã lấy tổng cộng {len(all_reviews)} bình luận.")
        files.download(file_name)
