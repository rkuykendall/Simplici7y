class Item < ActiveRecord::Base
  # title is the field name you want to convert to a permalink
  has_permalink :name 
  
  has_many :versions, :dependent => :destroy
  has_many :screenshots, :dependent => :destroy
  has_many :downloads, :dependent => :destroy
  has_many :reviews
  
  belongs_to :user
  
  validates_presence_of :name, :body, :user_id
  validates_format_of :name, :with => /\A[^<>]+\Z/i, :message => "can not contain brackets."

  # we now add the to_param method which Rails's routing uses
  def to_param
    permalink
  end
  
  def self.per_page
    10
  end

  def self.order_sql(k)
    if k == 'new'
      "version_created_at DESC"
    elsif k == 'old'
      "version_created_at ASC"
 
    elsif k == 'best'
      "ratings_weighted_count DESC"
    elsif k == 'worst'
      "ratings_weighted_count ASC"

    elsif k == 'popular'
      "downloads_count DESC"
    elsif k == 'unpopular'
      "downloads_count ASC"

    elsif k == 'loud'
      "reviews_count DESC"
    elsif k == 'quiet'
      "reviews_count ASC"

    else # Default to new
      "version_created_at DESC"
    end
  end

  
  def self.search(search = '', page = 1, order = 'new')
    paginate :page => page, :order => order_sql(order), :conditions => [ 'name LIKE ? AND versions_count > 0', "%#{search}%"  ]
  end
  
  def self.find_by_tc(tc, search = '', page = 1, order = 'new')
    paginate :page => page, :order => order_sql(order), :conditions => [ 'name LIKE ? AND versions_count > 0 AND tc_id = ?', "%#{search}%", tc.id ]
  end

  def self.search_by_user(user, search = '', page = 1, order = 'new')
    paginate :page => page, :order => order_sql(order), :conditions => [ 'name LIKE ? AND user_id = ?', "%#{search}%", user ]
  end


  # def self.find_popular(args = {})
  #   find(:all, :select => 'tags.*, count(*) as popularity', 
  #     :limit => args[:limit] || 10,
  #     :joins => "JOIN taggings ON taggings.tag_id = tags.id",
  #     :conditions => args[:conditions],
  #     :group => "taggings.tag_id", 
  #     :order => "popularity DESC"  )
  # end
  

    
  def find_version
    versions.reverse[0]
  end

  def rand_screenshot
    screenshots.find(:first, :order => "rand()")
  end
end