class UsersController < ApplicationController
  before_filter :users_before, :only => [:edit, :update, :destroy]
  # Authentication & Variables

  # GET /users
  # GET /users.xml
  def index
    @users = User.find(:all, :order => 'admin DESC, login ASC', :conditions => [ 'items_count > 1 OR reviews_count > 1' ])
    
    respond_to do |format|
      format.html # index.rhtml
      format.xml  { render :xml => @users.to_xml }
    end
  end

  # GET /users/1
  # GET /users/1.xml
  def show
    @user = User.find_by_permalink(params[:id])
    @items = Item.search(params[:search], params[:page], params[:order], nil, @user)
    
    respond_to do |format|
      if current_user && current_user.admin == 1
        format.html { render :action => "show" }
      else
        format.html { render :template => "items/index" }
      end
      format.xml  { render :xml => @items.to_xml }
    end
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
    @user.save
    if @user.errors.empty?
      self.current_user = @user
      redirect_back_or_default('/')
      flash[:notice] = "Thanks for signing up!"
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