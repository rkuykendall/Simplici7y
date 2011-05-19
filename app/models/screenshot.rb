class Screenshot < ActiveRecord::Base
  belongs_to :item, :counter_cache => true
  
  file_column :file, :magick => { :versions => { "thumb" => "160x90" } }
  # file_column :file
  validates_file_format_of :file, :in => ["gif", "png", "jpg"]
  validates_presence_of :file, :message => "Missing screenshot file"
end
