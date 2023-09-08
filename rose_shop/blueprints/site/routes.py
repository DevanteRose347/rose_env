from flask import Blueprint, render_template, request, flash, redirect

#internal imports
from rose_shop.models import CAR, Customer, Order, db, car_schema, car_schema 
from rose_shop.forms import CarForm



#we need to instantiate our Blueprint object
site = Blueprint('site', __name__, template_folder='site_templates') #telling your blueprint where to load the html files 



#create our first route
@site.route('/')
def shop():

    shop = Car.query.all()
    customers = Customer.query.all()
    orders = Order.query.all()

    shop_stats = {
        'cars': len(shop),
        'sales': sum([order.order_total for order in orders]), #order totals was total cost of that specific order
        'customers' : len(customers)
    }

    return render_template('shop.html', shop=shop, stats=shop_stats) #basically displaying our shop.html page 



#create our CREATE route
@site.route('/shop/create', methods = ['GET', 'POST'])
def create():

    createform = CarForm()

    if request.method == 'POST' and createform.validate_on_submit():

        # try: 
        name = createform.name.data
        desc = createform.description.data
        image = createform.image.data
        price = createform.price.data
        quantity = createform.quantity.data 

        shop = Car(name, price, quantity, image, desc) #instantiating Car object

        db.session.add(shop)
        db.session.commit()

        flash(f"You have successfully created product {name}", category='success')
        return redirect('/')

        # except:
        #     flash("We were unable to process your request. Please try again", category='warning')
        #     return redirect('/shop/create')
        
    return render_template('create.html', form=createform)


#create our CREATE route
@site.route('/shop/update/<id>', methods = ['GET', 'POST'])
def update(id):

    updateform = CarForm()
    car = Car.query.get(id) #WHERE clause WHERE car.prod_id == id 

    if request.method == 'POST' and updateform.validate_on_submit():

        try: 
            car.name = updateform.name.data
            car.description = updateform.description.data
            car.set_image(updateform.image.data, updateform.name.data) #calling upon that set_image method to set our image!
            car.price = updateform.price.data
            car.quantity = updateform.quantity.data 

            

            db.session.commit() #commits the changes to our objects 

            flash(f"You have successfully updated car {car.name}", category='success')
            return redirect('/')

        except:
            flash("We were unable to process your request. Please try again", category='warning')
            return redirect('/shop/update')
        
    return render_template('update.html', form=updateform, car=car)


@site.route('/shop/delete/<id>')
def delete(id):

    product = Car.query.get(id)

    db.session.delete(car)
    db.session.commit()

    return redirect('/')