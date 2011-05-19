class Version < ActiveRecord::Base
  belongs_to :item, :counter_cache => true
  has_many :downloads
  has_many :reviews

  file_column :file
  validates_file_format_of :file, :in => ["zip"]
  validates_presence_of :file, :message => "Missing zip file"
end
