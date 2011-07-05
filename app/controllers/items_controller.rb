class ItemsController < ApplicationController
  before_filter :before_items, :only => [ :show, :edit, :update, :destroy ]
  before_filter :login_required, :only => [ :new, :create ]
  before_filter :authenticate, :only => [ :edit, :update, :destroy ]
  
  # THIS IS FOR DEV, AND SHOULD BE REMOVED
  before_filter :update_rating_relevancy, :only  => [ :show ]
  # :index, :show, :new, :create, :edit, :update, :destroy
  
  # GET /items
  # GET /items.xml 
  def index
    @items = Item.search(params)

    users = User.find(:all, :conditions => [ "login LIKE ?", "%#{params[:search]}%" ] )
    if users.count == 1
  	    flash[:notice] = "Were you looking for <a href='#{user_path(users.first.permalink)}'>#{users.first.login}</a>?"
    end

    respond_to do |format|
      format.html # index.html.erb
      format.rss { render :action => 'index.xml.builder' }
      format.xml  { render :xml => @items.to_xml }
    end
  end

  # GET /items/1
  # GET /items/1.xml
  def show    
    @screenshots = @item.screenshots
    @reviews = @item.reviews.find(:all, :order => 'created_at DESC')
    
    respond_to do |format|
      format.html # show.html.erb
      format.xml  { render :xml => @item.to_xml }
    end
  end

  # GET /items/new
  def new
    @item = Item.new

    respond_to do |format|
      format.html # new.html.erb
    end
  end

  # POST /items
  # POST /items.xml
  def create
    @item = Item.new(params[:item].merge(:user_id => current_user.id))
  
    respond_to do |format|
      if @item.save
        @item.tag_with params[:tags] if params[:tags]
        flash[:notice] = "<strong>#{@item.name}</strong> was successfully added, upload the first revision below."
      
        format.html { redirect_to new_item_version_url(@item) }
        format.xml do
          headers["Location"] = item_url(@item)
          render :nothing => true, :status => "201 Created"
        end
      else
        format.html { render :action => 'new' }
        format.xml  { render :xml => @item.errors.to_xml }
      end
    end
  end
  
  # GET /items/1/edit
  def edit
    respond_to do |format|
      format.html # edit.html.erb
    end
  end

  # PUT /items/1
  # PUT /items/1.xml
  def update
    respond_to do |format|
      if @item.update_attributes(params[:item])
        @item.tag_with params[:tags] if params[:tags]
        
        format.html { redirect_to users_url }
        format.xml  { render :nothing => true }
      else
        format.html { render :action => 'edit' }
        format.xml  { render :xml => @item.errors.to_xml }        
      end
    end
  end

  # DELETE /items/1
  # DELETE /items/1.xml
  def destroy
    @item = Item.find_by_permalink(params[:id]) 
    @item.destroy

    respond_to do |format|
      flash[:notice] = "<strong>#{params[:id]}</strong> has been destroyed."
      format.html { redirect_back_or_default('/')   }
      format.xml  { render :nothing => true }
    end
  end
  

private
  def before_items
    @item = Item.find_by_permalink(params[:id])
    raise ActiveRecord::RecordNotFound if @item == nil

    if @item.tc_id == 0
      @items = Item.search(params.merge!({:user => @user, :tc => @item}))
      render :action => 'index'
    elsif action_name != 'destroy'
      @version = @item.find_version if @item.find_version
      raise ActiveRecord::RecordNotFound if @version == nil
    end
  rescue ActiveRecord::RecordNotFound
    redirect_back_or_default('/')
    flash[:notice] = "Item #{params[:id]} does not exist, or has no initial revision."
  end

end