class ScreenshotsController < ApplicationController
  before_filter :set_variables
  before_filter :authenticate

  # GET /screenshots/new
  def new
    @child = @item.screenshots.build

    respond_to do |format|
      format.html # new.html.erb
    end
  end

  # GET /screenshots/1/edit
  def edit
    respond_to do |format|
      format.html # edit.html.erb
    end
  end

  # POST /screenshots
  # POST /screenshots.xml
  def create
    @child = @item.screenshots.build(params[:child])
  
    respond_to do |format|
      if @child.save
        flash[:notice] = "Your screenshot for #{@item.name} was successfully added."
      
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

  # PUT /screenshots/1
  # PUT /screenshots/1.xml
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

  # DELETE /screenshots/1
  # DELETE /screenshots/1.xml
  def destroy
    @child.destroy
    
    respond_to do |format|
      format.html { redirect_back_or_default('/')       }
      format.xml  { render :nothing => true }
    end
  end
end