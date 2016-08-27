# Filters added to this controller apply to all controllers in the application.
# Likewise, all the methods added will be available for all controllers.

class ApplicationController < ActionController::Base
  helper :all # include all helpers, all the time
  
  # Be sure to include AuthenticationSystem in Application Controller instead
  include AuthenticatedSystem

  # See ActionController::RequestForgeryProtection for details
  # Uncomment the :secret if you're not using the cookie session store
  protect_from_forgery # :secret => '2c6dbfbea87e21708f2985e38b89a8a8'
  
  # See ActionController::Base for details 
  # Uncomment this to filter the contents of submitted sensitive data parameters
  # from your application log (in this case, all fields with names like "password"). 
  # filter_parameter_logging :password
  
  def authenticate
    if @child && permission(@child)
      return true
    elsif params[:item_id] == nil && @item && permission(@item)
      return true
    elsif params[:id] == nil && @item && permission(@item)
      return true
    else
      flash[:notice] = "Access denied."  
      access_denied
    end
  end
    
  def set_variables
    if params[:item_id] && params[:id]
      @item = Item.find_by_permalink(params[:item_id])
      @child = instance_variable_set("@#{controller_name}", current_model.find(params[:id])) if params[:id]
      raise ActiveRecord::RecordNotFound if @child == nil
    elsif params[:item_id]
      @item = Item.find_by_permalink(params[:item_id])
    else
      @item = Item.find_by_permalink(params[:id])
    end

    raise ActiveRecord::RecordNotFound if @item == nil
  rescue ActiveRecord::RecordNotFound
    flash[:notice] = "Error: Record Not Found."  
    if @item
      redirect_to item_url(@item)
    else
      redirect_back_or_default('/')
    end
  end
  
  def update_rating_relevancy
    reviews = @item.reviews.find(:all, :order => 'created_at DESC')
    version = @item.find_version

    reviews.each_with_index do |review, index|
        # Start at zero
        review.relevancy = 0
        
        # If it's an old version, bump it to 1
        review.relevancy = 1 if review.version_id != version.id
        
        # If there's a newer review, bump it to 3
        (0...index).each do |r|
          reviews[index].relevancy = 2 if reviews[r].user_id == review.user_id
        end

        # If it's by the owner, bump it to 2
        review.relevancy = 2 if review.user_id == @item.user_id
    end
    reviews.each(&:save!)
  end

private
  def current_model
    Object.const_get controller_name.classify
  end

  def params_hash
    params[controller_name.to_sym]
  end
end
