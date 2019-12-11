## 冒泡排序

重复的遍历数组, 每次遍历比较两个相邻的元素, 如果顺序错误(増序或者降序)就交换它们的位置. 这样的遍历直到没有再需要交换的元素为止.

```javascript
let arr = [ 50, 48, 47, 46, 44, 38, 36, 27, 26, 19, 15, 5, 4, 3, 2 ]
console.log('数组长度: ', arr.length)
let switchCount = 0
let count = 0
do {
 switchCount = 0
 for (let i = 0; i < arr.length - 1; i++) {
 if (arr[i] < arr[i + 1]) {
 /*temp = arr[i]
 arr[i] = arr[i + 1]
 arr[i + 1] = temp*/
 [arr[i], arr[i + 1]] = [arr[i + 1], arr[i]]
 console.log(count++)
 switchCount = i + 1
 }
 }
} while (switchCount !== 0)
console.log(arr)
```

## 代码测试

```java
import java.util.*;
class SubarrayProductLessThanK {
  public static List<List<Integer>> findSubarrays(int[] arr, int target) {
    List<List<Integer>> result = new ArrayList<>();
    int product = 1, left = 0;
    for (int right = 0; right < arr.length; right++) {
      product *= arr[right];
      while (product >= target && left < arr.length)
        product /= arr[left++];
      // since the product of all numbers from left to right is less than the target therefore,
      // all subarrays from lef to right will have a product less than the target too; to avoid
      // duplicates, we will start with a subarray containing only arr[right] and then extend it
      List<Integer> tempList = new LinkedList<>();
      for (int i = right; i >= left; i--) {
        tempList.add(0, arr[i]);
        result.add(new ArrayList<>(tempList));
      }
    }
    return result;
  }

  public static void main(String[] args) {
    System.out.println(SubarrayProductLessThanK.findSubarrays(new int[] { 2, 5, 3, 10 }, 30));
    System.out.println(SubarrayProductLessThanK.findSubarrays(new int[] { 8, 2, 6, 5 }, 50));
  }
}
```
