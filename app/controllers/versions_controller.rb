class VersionsController < ApplicationController
  before_filter :set_variables, :only => [ :new, :create, :edit, :update ]
  before_filter :authenticate, :only => [ :new, :create, :edit, :update ]
  after_filter :update_rating_relevancy, :only  => [ :create ]
  # :new, :create

  # GET /versions/new
  def new
    @child = @item.versions.build

    respond_to do |format|
      format.html # new.html.erb
    end
  end

  # GET /versions/1/edit
  def edit
    respond_to do |format|  
      format.html # edit.html.erb
    end
  end

  # POST /versions
  # POST /versions.xml
  def create
    @child = @item.versions.build(params[:child])
  
    respond_to do |format|
      if @child.save
        flash[:notice] = "#{@item.name} version #{@child.name} was successfully added. Upload any Screenshots below."
        @item.update_attributes(:version_created_at => Time.now)

        format.html { redirect_to new_item_screenshot_url(@item) }
        format.xml do
          headers["Location"] = new_item_screenshot_url_url(@item)
          render :nothing => true, :status => "201 Created"
        end
      else
        format.html { render :action => 'new' }
        format.xml  { render :xml => @child.errors.to_xml }
      end
    end
  end

  # PUT /versions/1
  # PUT /versions/1.xml
  def update
    respond_to do |format|
      if @child.update_attributes(params[:child])
        format.html { redirect_to users_url }
        format.xml  { render :nothing => true }
      else
        format.html { render :action => 'edit' }
        format.xml  { render :xml => @child.errors.to_xml }        
      end
    end
  end

  # # DELETE /versions/1
  # # DELETE /versions/1.xml
  # def destroy
  #   @version.destroy
  #   
  #   respond_to do |format|
  #     format.html { redirect_back_or_default('/')  }
  #     format.xml  { render :nothing => true }
  #   end
  # end

end