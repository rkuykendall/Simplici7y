class Item < ActiveRecord::Base
  # title is the field name you want to convert to a permalink
  has_permalink :name 
  
  has_many :versions, :dependent => :destroy
  has_many :screenshots, :dependent => :destroy
  has_many :downloads, :dependent => :destroy
  has_many :reviews
  
  belongs_to :user
  
  validates_presence_of :name, :body, :user_id
  validates_format_of :name, :with => /\A[^<>]+\Z/i, :message => "Brackets are not allowed in the name."
  validates_format_of :tags, :with => /\A[A-Za-z ]+\Z/i, :message => "Only alphanumeric tags allowed."

  # we now add the to_param method which Rails's routing uses
  def to_param
    permalink
  end
  
  def self.per_page
    10
  end

  def self.find_by_tc(tc, search, page)
    if search
      paginate :page => page, :order => 'version_created_at DESC', :conditions => [ 'name LIKE ? AND tc_id = ? AND versions_count > 0', "%#{search}%", tc.id ]
    else
      paginate :page => page, :order => 'version_created_at DESC', :conditions => [ 'tc_id = ? AND versions_count > 0', tc.id ]
    end
  end
  
  def self.search(search, page)
    if search
      paginate :page => page, :order => 'version_created_at DESC', :conditions => [ 'name LIKE ? AND versions_count > 0', "%#{search}%" ]
    else
      paginate :page => page, :order => 'version_created_at DESC', :conditions => [ 'versions_count > 0' ]
    end
  end
  
  def self.search_by_user(user, search, page)    
    if search
      paginate :page => page, :order => 'version_created_at DESC', :conditions => [ 'name LIKE ? AND user_id = ?', "%#{search}%", user ]
    else
      paginate :page => page, :order => 'version_created_at DESC', :conditions => [ 'user_id = ?', user ]
    end
  end

    
  def find_version
    versions.reverse[0]
  end

  def rand_screenshot
    screenshots.find(:first, :order => "rand()")
  end
end