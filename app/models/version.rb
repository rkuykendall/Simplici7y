class Version < ActiveRecord::Base
  belongs_to :item, :counter_cache => true
  has_many :downloads
  has_many :reviews

  file_column :file
  validates_file_format_of :file, :in => ["zip", "tgz", "tar", "gz"]

  # validates_presence_of :file, :message => "upload is missing a compressed file."
  validate :content?

  def content?
    if %w(file link).all?{|attr| self[attr].blank?}
      errors.add_to_base("Version is missing a compressed file or link.")
    end
  end
  
end
