class ReviewsController < ApplicationController
  before_filter :set_variables, :only => [ :new, :create, :edit, :update, :destroy ]
  before_filter :before_reviews, :only => [ :new, :create, :edit, :update, :destroy ]
  before_filter :login_required, :only => [:new, :create]
  before_filter :authenticate, :only => [ :edit, :update, :destroy ]
  # :index, :new, :create, :edit, :update, :destroy
  after_filter :update_rating_relevancy, :only  => [:create, :update, :destroy]
  after_filter :update_rating_counts, :only => [:create, :update, :destroy]

  # GET /reviews
  # GET /reviews.xml
  def index
    @reviews = Review.paginate :page => params[:page], :order => 'created_at DESC'
    
    respond_to do |format|
      format.html # index.rhtml
      format.rss { render :action => 'index.xml.builder' }
      format.xml  { render :xml => @reviews.to_xml }
    end
  end

  # GET /reviews/new
  def new
    @child = @item.reviews.build

    respond_to do |format|
      format.html # new.html.erb
    end
  end

  # POST /reviews
  # POST /reviews.xml
  def create
    @child = @item.reviews.build(params[:child].merge(
              :version_id => @item.find_version.id,
              :user_id => current_user.id))
  
    respond_to do |format|
      if @child.save
        flash[:notice] = "Your review for #{@item.name} was successfully added."
      
        format.html { redirect_to item_url(@item) }
        format.xml do
          headers["Location"] = item_url(@item)
          render :nothing => true, :status => "201 Created"
        end
      else
        format.html { render :action => 'new' }
        format.xml  { render :xml => @child.errors.to_xml }
      end
    end
  end

  # GET /reviews/1/edit
  def edit
    respond_to do |format|
      format.html # edit.html.erb
    end
  end

  # PUT /reviews/1
  # PUT /reviews/1.xml
  def update
    respond_to do |format|
      if @child.update_attributes(params[:child])
        format.html { redirect_to item_url(@item) }
        format.xml  { render :nothing => true }
      else
        format.html { render :action => 'edit' }
        format.xml  { render :xml => @child.errors.to_xml }        
      end
    end
  end

  # DELETE /reviews/1
  # DELETE /reviews/1.xml
  def destroy
    @child.destroy
    
    respond_to do |format|
      format.html { redirect_back_or_default(item_url(@item)) }
      format.xml  { render :nothing => true }
    end
  end

private
  
  def before_reviews
    if permission(@item) && admin? == false
      redirect_back_or_default('/')
      flash[:notice] = "Can't review your own upload."
    end
  end

  def update_rating_counts
    total = 0.0
    average = 0.0
    weighted = 0.0
    reviews = @item.reviews.find(:all, :conditions => [ 'relevancy < 2' ])
    count = reviews.length.to_f

    if count > 0
      for review in reviews
        total += review.rating
      end
      
      average = total / count
      weighted = average + ( average - 2.5 ) * ( count / 10.0 )
    end

    @item.update_attributes(:ratings_count => average, :ratings_weighted_count => weighted)
  end
  
end