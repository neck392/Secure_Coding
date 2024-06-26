import streamlit as st
import requests
from datetime import datetime

def initialize_session_state():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'initialized' not in st.session_state:
        st.session_state.initialized = False

def main():
    if not st.session_state.initialized:  
        st.session_state.initialized = True 

    st.title('Welcome to Simple Shopping Mall')
    st.write('This is a simple shopping mall where you can buy a variety of products.')

    if not st.session_state.logged_in:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader('Login')
            username = st.text_input('Username')
            password = st.text_input('Password', type='password')
            if st.button('Login'):
                try:
                    response = requests.get('http://localhost:8000/login', params={"username": username, "password": password})
                    if response.status_code == 200:
                        st.session_state.logged_in = True
                        st.session_state.user = response.json()
                        st.success(f"Welcome back, {st.session_state.user['username']}!")
                        st.experimental_rerun()
                    else:
                        st.error("Invalid username or password.")
                except requests.RequestException as e:
                    st.error(f"Error connecting to server: {e}")

        with col2:
            st.subheader('Sign Up')
            new_username = st.text_input('New Username')
            new_password = st.text_input('New Password', type='password')
            full_name = st.text_input('Full Name')
            address = st.text_input('Address')
            payment_info = st.text_input('Payment Info')
            if st.button('Sign Up'):
                try:
                    response = requests.post('http://localhost:8000/register', params={
                        "username": new_username,
                        "password": new_password,
                        "role": "user",
                        "full_name": full_name,
                        "address": address,
                        "payment_info": payment_info
                    })
                    if response.status_code == 200:
                        st.success(response.json()["message"])
                    else:
                        st.error("Failed to sign up.")
                except requests.RequestException as e:
                    st.error(f"Error connecting to server: {e}")

    if st.session_state.logged_in and st.session_state.user is not None:
        if st.session_state.user.get("role") == 'admin':
            st.sidebar.subheader('Admin Menu')
            menu = ['Home', 'Add Product', 'Delete Product', 'All Purchases Log', 'User Information']
            choice = st.sidebar.selectbox('Menu', menu)

            if choice == 'Home':
                st.subheader('All Products')
                try:
                    response = requests.get('http://localhost:8000/products')
                    response.raise_for_status()
                    products = response.json()
                    for product in products:
                        st.write(f"Name: {product['name']}, Category: {product['category']}, Price: ${product['price']}")
                        if 'thumbnail_url' in product and product['thumbnail_url'] != '':
                            st.image(product['thumbnail_url'], width=200)
                except requests.RequestException as e:
                    st.error(f"Error fetching products: {e}")

            elif choice == 'Add Product':
                st.subheader('Add a New Product')
                with st.form(key='add_product_form'):
                    name = st.text_input('Product Name')
                    category = st.text_input('Category')
                    price = st.number_input('Price', min_value=0.0)
                    thumbnail_url = st.text_input('Thumbnail URL')
                    submit_button = st.form_submit_button(label='Add')
                
                    if submit_button:
                        try:
                            add_product_response = requests.post('http://localhost:8000/add_product', json={
                                "name": name,
                                "category": category,
                                "price": price,
                                "thumbnail_url": thumbnail_url
                            })
                            if add_product_response.status_code == 200:
                                st.success(add_product_response.json()["message"])
                            else:
                                st.error("Failed to add product.")
                        except requests.RequestException as e:
                            st.error(f"Error connecting to server: {e}")

            elif choice == 'Delete Product':
                st.subheader('Delete a Product')
                try:
                    response = requests.get('http://localhost:8000/products')
                    response.raise_for_status()
                    products = response.json()
                    product_names = [product['name'] for product in products]
                    
                    selected_product = st.selectbox('Select a product to delete', product_names)
                    if st.button('Delete'):
                        try:
                            delete_response = requests.delete(f"http://localhost:8000/products/{selected_product}")
                            if delete_response.status_code == 200:
                                st.success(f"Successfully deleted product: {selected_product}")
                                st.experimental_rerun()
                            else:
                                st.error(f"Failed to delete product: {selected_product}")
                        except requests.RequestException as e:
                            st.error(f"Error connecting to server: {e}")
                except requests.RequestException as e:
                    st.error(f"Error fetching products: {e}")

            elif choice == 'All Purchases Log':
                st.subheader('All Purchases Log')
                try:
                    response = requests.get('http://localhost:8000/purchases')
                    response.raise_for_status()
                    purchases = response.json()
                    if purchases:
                        for purchase in purchases:
                            st.write(f"Buyer ID: {purchase['buyer_id']}, Product ID: {purchase['product_id']}, Purchase Time: {purchase['purchase_time']}, Payment Status: {purchase['payment_status']}, Buyer Address: {purchase['buyer_address']}")
                    else:
                        st.write("No purchases found.")
                except requests.RequestException as e:
                    st.error(f"Error fetching purchases: {e}")

            elif choice == 'User Information':
                st.subheader('User Information')
                try:
                    response = requests.get('http://localhost:8000/users')
                    response.raise_for_status()
                    users = response.json()
                    for user in users:
                        st.write(f"Username: {user['username']}, Full Name: {user['full_name']}, Address: {user['address']}, Payment Info: {user['payment_info']}")
                except requests.RequestException as e:
                    st.error(f"Error fetching users: {e}")

            if st.sidebar.button('Logout'):
                st.session_state.logged_in = False
                st.session_state.user = None
                st.success('You have been logged out.')
                st.experimental_rerun()

        else:
            st.sidebar.subheader('User Menu')
            menu = ['Home', 'Buy Products', 'My Page']
            choice = st.sidebar.selectbox('Menu', menu)

            if choice == 'Home':
                st.subheader('All Products')
                try:
                    response = requests.get('http://localhost:8000/products')
                    response.raise_for_status()
                    products = response.json()
                    for product in products:
                        st.write(f"Name: {product['name']}, Category: {product['category']}, Price: ${product['price']}")
                        if 'thumbnail_url' in product and product['thumbnail_url'] != '':
                            st.image(product['thumbnail_url'], width=200)
                except requests.RequestException as e:
                    st.error(f"Error fetching products: {e}")

            elif choice == 'Buy Products':
                st.subheader('Buy Products')
                try:
                    response = requests.get('http://localhost:8000/products')
                    response.raise_for_status()
                    products = response.json()
                    selected_product = st.selectbox('Select a product', [product['name'] for product in products])
                    user_address = st.text_input('Home Address')
                    user_payment_info = st.text_input('Payment Info')
                    if st.button('Buy'):
                        try:
                            purchase_response = requests.post('http://localhost:8000/add_purchase', json={
                                "buyer_id": st.session_state.user["id"],
                                "product_id": next(product["id"] for product in products if product["name"] == selected_product),
                                "purchase_time": datetime.now().isoformat(),
                                "payment_status": "Completed",
                                "buyer_address": user_address
                            })
                            if purchase_response.status_code == 200:
                                st.success(f'You have successfully purchased {selected_product}! Address: {user_address}, Payment Info: {user_payment_info}')
                            else:
                                st.error("Failed to complete purchase.")
                        except requests.RequestException as e:
                            st.error(f"Error connecting to server: {e}")
                except requests.RequestException as e:
                    st.error(f"Error fetching products: {e}")

            elif choice == 'My Page':
                st.subheader('My Page')
                st.write(f'Username: {st.session_state.user["username"]}')
                st.write(f'Full Name: {st.session_state.user["full_name"]}')
                st.write(f'Address: {st.session_state.user["address"]}')
                st.write(f'Payment Info: {st.session_state.user["payment_info"]}')
                
                with st.form(key='edit_user_info_form'):
                    new_username = st.text_input('New Username', value=st.session_state.user["username"])
                    new_full_name = st.text_input('Full Name', value=st.session_state.user["full_name"])
                    new_address = st.text_input('Address', value=st.session_state.user["address"])
                    new_payment_info = st.text_input('Payment Info', value=st.session_state.user["payment_info"])
                    submit_button = st.form_submit_button(label='Update Info')

                    if submit_button:
                        try:
                            response = requests.post('http://localhost:8000/update_user_info', params={
                                "username": new_username,
                                "full_name": new_full_name,
                                "address": new_address,
                                "payment_info": new_payment_info
                            })
                            if response.status_code == 200:
                                st.success('User information updated successfully!')
                                st.session_state.user["username"] = new_username
                                st.session_state.user["full_name"] = new_full_name
                                st.session_state.user["address"] = new_address
                                st.session_state.user["payment_info"] = new_payment_info
                                st.experimental_rerun()
                            else:
                                st.error("Failed to update user information.")
                        except requests.RequestException as e:
                            st.error(f"Error connecting to server: {e}")

            if st.sidebar.button('Logout'):
                st.session_state.logged_in = False
                st.success('You have been logged out.')
                st.experimental_rerun()

initialize_session_state()

if __name__ == '__main__':
    main()    