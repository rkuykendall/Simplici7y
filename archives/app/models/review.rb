class Review < ActiveRecord::Base
  belongs_to :item, :counter_cache => true
  belongs_to :version
  belongs_to :user
  
  validates_presence_of :title, :rating, :body, :item_id, :version_id, :user_id
  
  def mark_body
    if self.body != nil
      BlueCloth::new(self.body).to_html
    end
  end
end
