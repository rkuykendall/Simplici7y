class DownloadsController < ApplicationController
  include FileColumnHelper
  before_filter :set_variables
  
  def create
    @version = @item.find_version

    @child =  @item.downloads.build
              @child.version_id = @version.id
              @child.user_id = current_user.id if current_user
    
    respond_to do |format|
      if @child.save
        format.html { redirect_to url_for_file_column(@version, "file") }
        format.xml do
          headers["Location"] = url_for_file_column(@version, "file")
          render :nothing => true, :status => "201 Created"
        end
      else
        flash[:notice] = "Problems with download."
        redirect_to item_url(@item)
        format.xml  { render :xml => @child.errors.to_xml }
      end
    end
  rescue ActiveRecord::RecordInvalid
    redirect_to item_url(@item)
  end

end