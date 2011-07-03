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

  def self.order_sql(k, conditions)
    if k == 'new'
      "version_created_at DESC"
    elsif k == 'old'
      "version_created_at ASC"
 
    elsif k == 'best'
      conditions[0] += ' AND reviews_count > 0'
      "ratings_weighted_count DESC"
    elsif k == 'worst'
      conditions[0] += ' AND reviews_count > 0'
      "ratings_weighted_count ASC"

    elsif k == 'popular'
      "downloads_count DESC"
    elsif k == 'unpopular'
      "downloads_count ASC"

    elsif k == 'day'
      conditions[0] += ' AND downloads_day_count > 0'
      "downloads_day_count DESC"
    elsif k == 'week'
      conditions[0] += ' AND downloads_week_count > 0'
      "downloads_week_count DESC"
    elsif k == 'month'
      conditions[0] += ' AND downloads_month_count > 0'
      "downloads_month_count DESC"

    elsif k == 'loud'
      conditions[0] += ' AND reviews_count > 0'
      "reviews_count DESC"
    elsif k == 'quiet'
      "reviews_count ASC"

    else # Default to new
      "version_created_at DESC"
    end
  end
  
  
  # This is that passing params thing
  
  # @tags = Tag.find_popular(:limit => 50)     
  
  # def self.find_popular(args = {})
  #   find(:all, :select => 'tags.*, count(*) as popularity', 
  #     :limit => args[:limit] || 10,
  #     :joins => "JOIN taggings ON taggings.tag_id = tags.id",
  #     :conditions => args[:conditions],
  #     :group => "taggings.tag_id", 
  #     :order => "popularity DESC"  )
  # end

  
  def self.search(search = '', page = 1, order = 'new', tc = nil, user = nil)
    conditions = [ 'name LIKE ?', "%#{search}%" ]

    if(!user)
      conditions[0] += ' AND versions_count > 0'
    end

    if (tc)
      conditions[0] += ' AND tc_id = ?'
      conditions <<  tc.id
    elsif(user)
      conditions[0] += ' AND user_id = ?'
      conditions <<  user
    end
      
    paginate :page => page, :order => order_sql(order,conditions), :conditions => conditions
  end

    
  def find_version
    versions.reverse[0]
  end

  def rand_screenshot
    screenshots.find(:first, :order => "rand()")
  end
end