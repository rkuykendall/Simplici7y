class DownloadsController < ApplicationController
  include FileColumnHelper
  before_filter :set_variables
  
  def create
    @version = @item.find_version

    @child =  @item.downloads.build
              @child.version_id = @version.id
              @child.user_id = current_user.id if current_user
    
    if @version.file != nil
      url = url_for_file_column(@version, "file");
    elsif @version.link != ""
      url = @version.link
    end
    
    respond_to do |format|
      if @child.save and url != nil
        format.html { redirect_to url }
        format.xml do
          headers["Location"] = url
          render :nothing => true, :status => "201 Created"
        end
      else
        format.html {
          flash[:notice] = "There was a problem with the download."
          redirect_to item_url(@item)
        }
        format.xml  { render :xml => @child.errors.to_xml }
      end
    end
  rescue ActiveRecord::RecordInvalid
    redirect_to item_url(@item)
  end

end