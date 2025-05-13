import pandas as pd

# # اقرأ الملف الأصلي
# df = pd.read_csv("filtered_sorted_file.csv")
# df.describe()
# # شيل الصفوف اللي فيها أي خلايا فاضية
# df_cleaned = df.dropna()
#
# # احفظ الملف الجديد
# df_cleaned.to_csv("books.csv", index=False)

#
# # اقرأ الملف
df = pd.read_csv("filtered-books.csv")

# احسب التكرار ورتبهم من الأكثر للأقل
category_counts = df["categories"].value_counts()

# اطبعهم
print(category_counts)


# import pandas as pd
#
# # اقرأ ملف CSV
# df = pd.read_csv("all-books.csv")
#
# # رتب حسب عمودين، مثلا: category تصاعدي و Price تنازلي
# df_sorted = df.sort_values(by=["categories", "average_rating"], ascending=[True, False])
#
# # احفظ الملف الجديد بعد الترتيب
# df_sorted.to_csv("all-books-sorted.csv", index=False)



# import pandas as pd
#
# # اقرأ ملف CSV
# df = pd.read_csv("books.csv")
#
# # احسب عدد التكرارات لكل category
# category_counts = df["categories"].value_counts()
#
# # احتفظ بس بالـ categories اللي متكررة 15 مرة أو أكتر
# valid_categories = category_counts[category_counts >= 15].index
#
# # صفّي الداتا على أساس التصنيفات دي
# filtered_df = df[df["categories"].isin(valid_categories)]
#
# # رتب الداتا بعد كده حسب category و Price
# sorted_df = filtered_df.sort_values(by=["categories", "average_rating"], ascending=[True, False])
#
# # احفظ الملف النهائي
# sorted_df.to_csv("filtered-books.csv", index=False)
