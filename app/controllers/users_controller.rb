class UsersController < ApplicationController
  before_filter :users_before, :only => [:edit, :update, :destroy]
  # Authentication & Variables

  # GET /users
  # GET /users.xml
  def index
    @users = User.find(:all, :order => 'admin DESC, login ASC', :conditions => [ 'items_count > 0 OR reviews_count > 1' ])
    
    respond_to do |format|
      format.html # index.rhtml
      format.xml  { render :xml => @users.to_xml }
    end
  end

  # GET /users/1
  # GET /users/1.xml
  def show
    @user = User.find_by_permalink(params[:id])
    raise ActiveRecord::RecordNotFound if @user == nil

    @items = Item.search(params.merge!({:user => @user, :per_page => 50}))
    @reviews = Review.find(:all, :order => 'created_at DESC', :conditions => [ 'user_id = ?', @user.id ] )
    
    respond_to do |format|
      if permission(@user)
        format.html { render :action => "manage" }
      else
        format.html { render :action => "show" }
      end
      format.xml  { render :xml => @items.to_xml }
    end
    
  rescue ActiveRecord::RecordNotFound
    redirect_back_or_default('/')
    flash[:notice] = "User #{params[:id]} does not exist."
  end

  # render new.rhtml
  def new
  end
  
  def create
    cookies.delete :auth_token
    # protects against session fixation attacks, wreaks havoc with 
    # request forgery protection.
    # uncomment at your own risk
    # reset_session
    
    @user = User.new(params[:user])

    if @user.errors.empty? && verify_recaptcha(:model => @user, :message => "reCAPTCHA was incorrect, please try again.")
      @user.save
      self.current_user = @user
      redirect_back_or_default('/')
      flash[:notice] = "Thanks for signing up! Welcome to Simplici7y."
    else
      render :action => 'new'
    end
  end

  # GET /users/1/edit  
  def edit  
  end
    
  def update
    respond_to do |format|
      if @user.update_attributes(params[:user])
        flash[:notice] = "User account saved successfully."
        format.html { redirect_to :action => "show" }
      else
        format.html { render :action => "edit" }
      end
    end
  end

private

  def users_before
    @user = User.find_by_permalink(params[:id])
    access_denied unless permission(@user)
  end

end