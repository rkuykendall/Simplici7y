require File.dirname(__FILE__) + '/../test_helper'

class TagTest < Test::Unit::TestCase
  fixtures :items  
  def setup
    @obj = Item.find(:first)
    @obj.tag_with "pale imperial"
  end

  def test_to_s
    assert_equal "imperial pale", Item.find(:first).tags.to_s
  end
  
end
