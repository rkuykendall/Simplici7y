class Download < ActiveRecord::Base
  belongs_to :version, :counter_cache => true
  belongs_to :item, :counter_cache => true
  belongs_to :user

  named_scope :last_day, :conditions => [ "created_at > ?", 1.day.ago ]
  named_scope :last_week, :conditions => [ "created_at > ?", 1.week.ago ]
  named_scope :last_month, :conditions => [ "created_at > ?", 1.month.ago ]
end
