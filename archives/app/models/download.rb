class Download < ActiveRecord::Base
  belongs_to :version, :counter_cache => true
  belongs_to :item, :counter_cache => true
  belongs_to :user
end
