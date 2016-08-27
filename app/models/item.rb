class Item < ActiveRecord::Base
  # title is the field name you want to convert to a permalink
  has_permalink :name 
  
  has_many :versions, :dependent => :destroy
  has_many :screenshots, :dependent => :destroy
  has_many :downloads, :dependent => :destroy
  has_many :reviews
  
  belongs_to :user, :counter_cache => true
  
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
      @title = "Testing day"
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
  
  def self.search(args = {})
    perpage = args[:per_page] || 10
    
    conditions = [ 'name LIKE ?', "%#{ args[:search] || '' }%" ] 

    if(!args[:user])
      conditions[0] += ' AND versions_count > 0'
    end

    if (args[:tc])
      conditions[0] += ' AND tc_id = ?'
      conditions <<  args[:tc].id
    elsif(args[:user])
      conditions[0] += ' AND user_id = ?'
      conditions << args[:user].id
    end
      
    paginate :page => args[:page], :order => order_sql(args[:order],conditions), :conditions => conditions, :per_page => perpage
  end
    
  def find_version
    versions.reverse[0]
  end

  def rand_screenshot
    screenshots.find(:first, :order => "rand()")
  end
end