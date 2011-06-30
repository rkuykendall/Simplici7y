class Hourly < ActiveRecord::Base
  # Code from example
  # post_ids = Post.find(:all, :conditions => ["created_at < ?", 5.minutes.ago])
  # 
  # if post_ids.size > 0
  #   Post.destroy(post_ids)
  #   puts "#{post_ids.size} posts have been deleted!"
  # end
  
  puts "Start!"
  
  @items = Item.find(:all, :conditions => ["versions_count > 0"])

  puts "Processing!"
  
  @items.each do |item|
    item.downloads_day_count = item.downloads.last_day.count
    item.downloads_week_count = item.downloads.last_week.count
    item.downloads_month_count = item.downloads.last_month.count
    item.save
  end

  puts "Finished!"

  # Code from downloads development
  # after_filter :calculate_counts
  #
  # def calculate_counts
  #   item = Item.find_by_permalink(params[:item_id])
  #   item.downloads_day_count = item.downloads.last_day.count
  #   item.downloads_week_count = item.downloads.last_week.count
  #   item.downloads_month_count = item.downloads.last_month.count
  #   item.save
  # end

end
