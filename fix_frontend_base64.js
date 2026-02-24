/**
 * 修复前端base64图像上传问题
 * 
 * 问题：前端使用 readAsDataURL() 返回完整的 data URL
 *       但后端期望纯base64字符串
 * 
 * 解决方案：从 data URL 中提取纯base64部分
 */

// 测试数据：模拟 readAsDataURL() 的输出
const dataURL = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/4gI0SUNDX1BST0ZJTEUAAQEAAAIkYXBwbAQAAABtbnRyUkdCIFhZWiAH4QAHAAcADQAWACBhY3NwQVBQTAAAAABBUFBMAAAAAAAAAAAAAAAAAAAAAAAA9tYAAQAAAADTLWFwcGwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABFkZXNjAAABUAAAAGJkc2NtAAABtAAABDZjcHJ0AAAF7AAAACN3dHB0AAAGEAAAABRyWFlaAAAGJAAAABRnWFlaAAAGOAAAABRiWFlaAAAGTAAAABRyVFJDAAAGYAAACAxhYXJnAAAObAAAACB2Y2d0AAAOjAAABhJuZGluAAAUoAAABj5jaGFkAAAZoAAAACxtbW9kAAAZxAAAAChiVFJDAAAGYAAACAxnVFJDAAAGYAAACAxhYWJnAAAObAAAACBhYWdnAAAObAAAACBkZXNjAAAAAAAAAAhEaXNwbGF5AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAbWx1YwAAAAAAAAAjAAAADGhySFIAAAAUAAABtGtvS1IAAAAMAAAByG5iTk8AAAASAAAB1GlkAAAAAAASAAAB5mh1SFUAAAAUAAAB+GNzQ1oAAAAWAAACDGRhREsAAAAcAAACIm5sTkwAAAAWAAACPmZpRkkAAAAQAAACVGl0SVQAAAAUAAACZHJvUk8AAAASAAACeGVzRVMAAAASAAACeGFyAAAAAAAUAAACinVrVUEAAAAcAAACnmhlSUwAAAAWAAACunpoVFcAAAAMAAAC0HZpVk4AAAAOAAAC3HNrU0sAAAAWAAAC6npoQ04AAAAMAAAC0HJ1UlUAAAAkAAADAG1zAAAAAAASAAADJGZyRlIAAAAWAAADPGRhREsAAAAcAAADTmxQTAAAAAMAAADXZWxHUgAAACIAAADac3ZTRQAAAAwAAADiemhUVwAAAA0AAADkamlUSwAAAAWAAADqHRoVEgAAAAMAAADvGNhRVMAAAAYAAAD0GVuQVUAAAAUAAADdmVzWEwAAAASAAACeGRlREUAAAAQAAAD6GVuVVMAAAASAAAD+HB0QlIAAAAYAAAECnBsUEwAAAASAAAEHmVsR1IAAAAiAAAENHN2U0UAAAAQAAAEPnRyVFIAAAAUAAAETnB0UFQAAAAWAAAEYmphSlAAAAAMAAAEeABMAEMARAAgAHUAIABiAG8AegBvAG++Zli7";

console.log("原始 data URL 长度:", dataURL.length);
console.log("原始 data URL 前100字符:", dataURL.substring(0, 100) + "...");

// 提取纯base64
const pureBase64 = dataURL.split(',')[1];
console.log("\n提取的纯base64长度:", pureBase64.length);
console.log("纯base64前100字符:", pureBase64.substring(0, 100) + "...");

// 验证base64格式
function isValidBase64(str) {
    try {
        // 检查是否是有效的base64
        const decoded = atob(str);
        console.log("\n✅ Base64解码成功");
        console.log("解码后长度:", decoded.length, "字节");
        return true;
    } catch (e) {
        console.log("\n❌ Base64解码失败:", e.message);
        return false;
    }
}

// 测试
isValidBase64(pureBase64);

// 修复前端代码的建议
console.log("\n" + "=".repeat(60));
console.log("前端代码修复建议");
console.log("=".repeat(60));

console.log(`
当前代码（DietTracking.tsx 第155-157行）：
  reader.onloadend = () => {
    setSelectedPhoto(reader.result as string);
    setShowPhotoModal(true);
  };
  reader.readAsDataURL(file);

应该改为：
  reader.onloadend = () => {
    const dataURL = reader.result as string;
    // 提取纯base64部分（去掉 data:image/jpeg;base64, 前缀）
    const pureBase64 = dataURL.split(',')[1];
    setSelectedPhoto(pureBase64);
    setShowPhotoModal(true);
  };
  reader.readAsDataURL(file);
`);

console.log("\n或者，更好的方法是创建一个工具函数：");
console.log(`
// utils/imageUtils.ts
export function extractBase64FromDataURL(dataURL: string): string {
  // dataURL格式: data:image/jpeg;base64,/9j/4AAQSkZJRg...
  const parts = dataURL.split(',');
  if (parts.length !== 2) {
    throw new Error('Invalid data URL format');
  }
  return parts[1];
}

export function createDataURLFromBase64(base64: string, mimeType: string = 'image/jpeg'): string {
  return \`data:\${mimeType};base64,\${base64}\`;
}

// 在组件中使用：
reader.onloadend = () => {
  const dataURL = reader.result as string;
  const pureBase64 = extractBase64FromDataURL(dataURL);
  setSelectedPhoto(pureBase64);
  setShowPhotoModal(true);
};
`);