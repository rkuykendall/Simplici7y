class Review < ActiveRecord::Base
  belongs_to :item, :counter_cache => true
  belongs_to :version
  belongs_to :user, :counter_cache => true
  
  validates_presence_of :title, :rating, :body, :item_id, :version_id, :user_id
  validates_format_of :title, :with => /\A[^<>]*\Z/i, :message => "can not contain brackets."
end
