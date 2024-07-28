from flask import Flask, render_template, request
import pickle 
from pandas import DataFrame
import numpy as np

#loaded pickled data
result_df=DataFrame()
pt= pickle.load(open('pt.pkl', 'rb'))
books=pickle.load(open('book.pkl','rb'))
similarity_scores=pickle.load(open('similarity_scores.pkl','rb'))


app= Flask(__name__)

#mapping the images
placeholder_image_url= "https://picsum.photos/id/870/200/300?grayscale&blur=2"
image_url_mapping ={ "Michael Crichton": "https://picsum.photos/seed/picsum/120/200", "Amy Tan": "https://picsum.photos/120/200", "Anna Quindlen":"https://picsum.photos/120/200/?blur", "Jack London": "https://picsum.photos/seed/picsum/120/200"}

#function to initialise the result_df for each time index route is called
def load_result_df():
    result_df=pickle.load(open('result.pkl', 'rb'))
    if not result_df.empty and all(col in result_df.columns for col in ['Book-Title', 'Book-Author', 'num-ratings', 'avg-ratings']):
        result_df['Image-URL-M'].fillna(placeholder_image_url, inplace=True)
        result_df.loc[result_df['Image-URL-M']=='', "Image-URL-M"]= placeholder_image_url
      
        for author, image_url in image_url_mapping.items():
            result_df.loc[result_df['Book-Author']==author, 'Image-URL-M']= image_url

        result_df=result_df.rename(columns= {'Book-Title': 'title','Book-Author': 'author' , 'Image-URL-M': 'image','num-ratings': 'votes', 'avg-ratings': 'rating' })

    else:
        print('DataFrame is empty or missing required columns')

    return result_df
        

@app.route('/')
def index():
        result_df=load_result_df()
        books=result_df.to_dict(orient= 'records')
        print('Books to display:')
        for book in books[:2]:
            print(book)
        return render_template('index.html', books= books)


@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')

@app.route('/recommend_books', methods=['POST'])
def recommend():
    user_input= request.form.get('user_input')

    if user_input in pt.index:
      index= np.where(pt.index == user_input)[0][0]
      similar_items= sorted(list(enumerate(similarity_scores[index])), key=lambda x:x[1], reverse=True)[1:5]

      data=[]
      for i in similar_items:
          item=[]
          temp_df =books[books['Book-Title']==pt.index[i[0]]]
          item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
          item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
          item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))

          data.append(item)

      print(data)

      return render_template('recommend.html', data=data)
    else:
        error_message=f"No book found with the title '{user_input}'. Please try another title."
        print(error_message)
        return render_template('recommend.html', error= error_message)
    


if __name__== '__main__':
    app.run(debug= True)