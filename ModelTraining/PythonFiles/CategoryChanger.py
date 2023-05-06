class CategoryChanger():
   categoryNames = [
       '1.47E+15', '8.21E+14', '1.67E+15', '7.58E+14', '6.25E+14',
       '6.06E+14', '1.55E+15', '8.95E+14', '1.83E+15', '1.57E+15',
       '1.79E+15', '1.56E+15', '1.53E+15', '6.79E+14', '1.38E+15',
       '6.77E+14', '8.00E+14', '2.15E+14', '1.58E+15', '6.87E+14',
       '1.66E+15', '9.31E+14', '3.94E+14', '8.07E+14', '6.14E+14',
       '1.27E+15', '1.09E+15', '7.13E+14', '1.30E+15', 'Electronics & computers',
       "Men\\'s clothing & shoes", 'Sport & outdoors', 'Car parts', 'Furniture', 'Books, films & music',
       'Tools', 'Mobile phones', 'Appliances','Baby & children', 'Garden',
       "Women\\'s clothing & shoes", 'Toys & games', '8.69E+14', 'Pet supplies'
       ]
    
   newCategoryNames = [
       'Rentals','Home Sales','Home Improvement Supplies','Vehicles','Family',
       'Toys & Games','Pet Supplies','Miscellaneous','Miscellaneous','Home Goods',
       'Electronics','Electronics','Hobbies','Home Improvement Supplies','Hobbies',
       'Musical Instruments','Garden & Outdoor','Apparel','Home Goods','Toys & Games',
       'Sporting Goods','Apparel','Hobbies','Vehicles','Home Goods',
       'Apparel','Vehicles','Vehicles','Vehicles', 'Electronics',
       'Apparel', 'Sporting Goods', 'Vehicles', 'Home Goods', 'Entertainment',
       'Home Improvement Supplies', 'Electronics', 'Electronics', 'Family', 'Garden & Outdoor',
       'Apparel', 'Toys & Games', 'Vehicles', 'Pet Supplies'
       ]
    
   def changeCategories(self, df):
      df['Category'] = [self.round_num(val) for val in df['Category']]
      return df['Category'].replace(self.categoryNames, self.newCategoryNames)
    
   def round_num(self, input):
      try:
        num = float(input)
      except ValueError:
         return input
      return "{:.2E}".format(num)
